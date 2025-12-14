"""Main pipeline orchestrator coordinating all components."""

import logging
from typing import Dict, Optional
import pandas as pd

from core.llm_client import LLMClient
from analyzer.structure_analyzer import StructureAnalyzer
from analyzer.semantic_analyzer import SemanticAnalyzer
from analyzer.ground_truth_comparator import GroundTruthComparator
from analyzer.analysis_report import AnalysisReport
from generator.code_generator import CodeGenerator
from executor.runner import CodeRunner
from validator.data_validator import DataValidator
from optimizer.code_optimizer import CodeOptimizer
from output.exporter import DataExporter
from learning.pattern_library import PatternLibrary
from utils.helpers import get_timestamp, save_json

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the entire Excel transformation pipeline."""

    def __init__(self, config: Dict):
        """
        Initialize pipeline orchestrator.

        Args:
            config: System configuration dictionary
        """
        self.config = config

        # Initialize LLM client
        self.llm_client = LLMClient(config['llm'])

        # Initialize components
        self.structure_analyzer = StructureAnalyzer(
            self.llm_client,
            config['analysis'].get('sample_rows', 50)
        )
        self.semantic_analyzer = SemanticAnalyzer(self.llm_client)
        self.ground_truth_comparator = GroundTruthComparator(self.llm_client)
        self.code_generator = CodeGenerator(self.llm_client)
        self.code_runner = CodeRunner()
        self.data_validator = DataValidator(config['validation']['accuracy_threshold'])
        self.code_optimizer = CodeOptimizer(self.llm_client)
        self.data_exporter = DataExporter()
        self.pattern_library = PatternLibrary()

        self.max_iterations = config['optimization']['max_iterations']
        self.enable_learning = config['optimization']['enable_learning']
        self.output_formats = config['output']['formats']
        self.save_artifacts = config['output']['save_artifacts']

    def run(self, messy_path: str, ground_truth_path: str, output_dir: str,
            check_library: bool = False) -> Dict:
        """
        Run the complete transformation pipeline.

        Args:
            messy_path: Path to messy Excel file
            ground_truth_path: Path to ground truth sample
            output_dir: Output directory for results
            check_library: Whether to check pattern library first

        Returns:
            Pipeline execution results
        """
        logger.info("="*80)
        logger.info("Starting Excel Transformation Pipeline")
        logger.info("="*80)

        timestamp = get_timestamp()
        results = {
            "timestamp": timestamp,
            "messy_file": messy_path,
            "ground_truth_file": ground_truth_path,
            "success": False
        }

        try:
            # Phase 1: Analysis
            logger.info("\n=== PHASE 1: LLM-POWERED ANALYSIS ===")

            logger.info("1.1 Structure Analysis...")
            structure = self.structure_analyzer.analyze(messy_path)

            logger.info("1.2 Semantic Analysis...")
            semantic = self.semantic_analyzer.analyze(messy_path, structure)

            logger.info("1.3 Transformation Planning...")
            transformation_plan = self.ground_truth_comparator.compare(
                structure, semantic, ground_truth_path
            )

            # Generate analysis report
            analysis_report = AnalysisReport.generate(
                structure, semantic, transformation_plan
            )

            if self.save_artifacts:
                analysis_path = f"{output_dir}/artifacts/analysis_{timestamp}.json"
                save_json(analysis_report, analysis_path)
                results['analysis_report'] = analysis_path

            # Check pattern library if requested
            if check_library and self.enable_learning:
                logger.info("\n=== CHECKING PATTERN LIBRARY ===")
                pattern = self.pattern_library.find_similar_pattern(analysis_report)

                if pattern:
                    logger.info(f"Found similar pattern: {pattern['pattern_id']}")
                    logger.info("Skipping code generation, using existing pattern...")

                    # TODO: Use pattern code directly
                    # For now, continue with generation

            # Phase 2: Code Generation
            logger.info("\n=== PHASE 2: DYNAMIC CODE GENERATION ===")

            code_path = self.code_generator.generate(
                analysis_report,
                messy_path,
                ground_truth_path
            )
            results['generated_code'] = code_path

            # Phase 3: Execution & Validation
            logger.info("\n=== PHASE 3: EXECUTION & VALIDATION ===")

            iteration = 0
            validation_passed = False
            current_code_path = code_path

            while iteration < self.max_iterations and not validation_passed:
                iteration += 1
                logger.info(f"\nIteration {iteration}/{self.max_iterations}")

                # Execute transformation
                output_path = f"{output_dir}/cleaned_data/cleaned_{timestamp}_iter{iteration}.csv"
                success, result_df, error_msg = self.code_runner.execute(
                    current_code_path,
                    messy_path,
                    output_path
                )

                if not success:
                    logger.error(f"Execution failed: {error_msg}")

                    if iteration < self.max_iterations:
                        logger.info("Attempting to optimize code...")
                        # Phase 4: Optimization
                        validation_report = {
                            "passed": False,
                            "error": error_msg,
                            "mismatches_sample": []
                        }
                        current_code_path = self.code_optimizer.optimize(
                            current_code_path,
                            validation_report
                        )
                        continue
                    else:
                        results['error'] = error_msg
                        break

                # Validate results
                logger.info("Validating results...")
                validation_report = self.data_validator.validate(
                    result_df,
                    ground_truth_path
                )

                if self.save_artifacts:
                    validation_path = f"{output_dir}/artifacts/validation_{timestamp}_iter{iteration}.json"
                    save_json(validation_report, validation_path)

                if validation_report['passed']:
                    logger.info("✓ Validation PASSED!")
                    validation_passed = True
                    results['validation_report'] = validation_report
                    results['final_code'] = current_code_path
                    results['cleaned_data'] = output_path
                    results['iterations'] = iteration

                    # Phase 5: Export & Learning
                    logger.info("\n=== PHASE 5: OUTPUT & LEARNING ===")

                    # Export to multiple formats
                    base_path = f"{output_dir}/cleaned_data/cleaned_{timestamp}"
                    exported_files = self.data_exporter.export(
                        result_df,
                        base_path,
                        self.output_formats
                    )
                    results['exported_files'] = exported_files

                    # Save pattern to library
                    if self.enable_learning:
                        logger.info("Saving successful pattern to library...")
                        pattern_id = self.pattern_library.save_pattern(
                            analysis_report,
                            current_code_path,
                            validation_report,
                            metadata={
                                "source_file": messy_path,
                                "ground_truth_file": ground_truth_path
                            }
                        )
                        results['pattern_id'] = pattern_id

                    results['success'] = True
                    break

                else:
                    logger.warning(f"✗ Validation failed: {validation_report['summary']}")

                    if iteration < self.max_iterations:
                        logger.info("Optimizing code based on validation failures...")
                        # Phase 4: Optimization
                        current_code_path = self.code_optimizer.optimize(
                            current_code_path,
                            validation_report
                        )
                    else:
                        logger.error("Max iterations reached. Transformation failed.")
                        results['validation_report'] = validation_report
                        results['final_code'] = current_code_path

            logger.info("\n" + "="*80)
            if results['success']:
                logger.info("✓ PIPELINE COMPLETED SUCCESSFULLY")
            else:
                logger.info("✗ PIPELINE FAILED")
            logger.info("="*80)

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            results['error'] = str(e)

        return results
