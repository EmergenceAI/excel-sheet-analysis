"""Generate comprehensive analysis report."""

import logging
from typing import Dict
from utils.helpers import save_json, get_timestamp

logger = logging.getLogger(__name__)


class AnalysisReport:
    """Generates and saves comprehensive analysis reports."""

    @staticmethod
    def generate(structure: Dict, semantic: Dict, transformation: Dict,
                 output_path: str = None) -> Dict:
        """
        Generate comprehensive analysis report.

        Args:
            structure: Structure analysis results
            semantic: Semantic analysis results
            transformation: Transformation plan
            output_path: Path to save report (None for auto-generate)

        Returns:
            Complete analysis report dictionary
        """
        logger.info("Generating comprehensive analysis report")

        report = {
            "timestamp": get_timestamp(),
            "structure_analysis": structure,
            "semantic_analysis": semantic,
            "transformation_plan": transformation,
            "summary": {
                "source_file": structure.get('analyzed_file'),
                "target_file": transformation.get('ground_truth_file'),
                "layout_type": structure.get('layout_type'),
                "fact_type": semantic.get('fact_type'),
                "complexity": transformation.get('complexity_estimate'),
                "confidence_scores": {
                    "structure": structure.get('confidence_score'),
                    "semantic": semantic.get('confidence_score'),
                    "transformation": transformation.get('confidence_score')
                }
            }
        }

        # Save report if path provided
        if output_path:
            save_json(report, output_path)
            logger.info(f"Analysis report saved to: {output_path}")

        return report
