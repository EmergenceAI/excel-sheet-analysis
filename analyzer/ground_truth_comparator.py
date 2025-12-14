"""Compare source Excel with ground truth to plan transformation."""

import logging
from typing import Dict
import pandas as pd
from core.llm_client import LLMClient
from utils.excel_reader import ExcelReader

logger = logging.getLogger(__name__)


class GroundTruthComparator:
    """Compares source with ground truth and plans transformation."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize ground truth comparator.

        Args:
            llm_client: LLM client for AI analysis
        """
        self.llm = llm_client

    def compare(self, source_structure: Dict, source_semantic: Dict,
                ground_truth_path: str) -> Dict:
        """
        Compare source with ground truth and plan transformation.

        Args:
            source_structure: Structure analysis of source
            source_semantic: Semantic analysis of source
            ground_truth_path: Path to ground truth Excel file

        Returns:
            Transformation plan dictionary
        """
        logger.info(f"Comparing with ground truth: {ground_truth_path}")

        # Read ground truth sample
        df_truth = pd.read_excel(ground_truth_path, nrows=100)
        target_columns = list(df_truth.columns)
        target_sample = df_truth.head(20).to_string()

        # Load prompt template
        with open('analyzer/prompts/transformation_planning.txt', 'r') as f:
            prompt_template = f.read()

        # Build prompt
        prompt = prompt_template.format(
            source_structure=str(source_structure),
            source_semantic=str(source_semantic),
            target_columns=target_columns,
            target_sample=target_sample
        )

        # Get LLM analysis
        logger.info("Sending transformation planning request to LLM...")
        plan = self.llm.generate_json(
            prompt,
            system_prompt="You are an expert data transformation architect. Design precise transformation plans."
        )

        # Add metadata
        plan['ground_truth_file'] = ground_truth_path
        plan['target_columns'] = target_columns

        logger.info(f"Transformation plan complete. Complexity: {plan.get('complexity_estimate', 'N/A')}")

        return plan
