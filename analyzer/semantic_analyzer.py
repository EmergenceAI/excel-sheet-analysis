"""Semantic analyzer to understand business meaning of Excel data."""

import logging
from typing import Dict
import pandas as pd
from core.llm_client import LLMClient
from utils.excel_reader import ExcelReader

logger = logging.getLogger(__name__)


class SemanticAnalyzer:
    """Analyzes semantic meaning and business context of Excel data."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize semantic analyzer.

        Args:
            llm_client: LLM client for AI analysis
        """
        self.llm = llm_client
        self.excel_reader = ExcelReader()

    def analyze(self, excel_path: str, structure_analysis: Dict, sheet_name: str = None) -> Dict:
        """
        Analyze semantic meaning of Excel data.

        Args:
            excel_path: Path to Excel file
            structure_analysis: Results from structure analysis
            sheet_name: Sheet to analyze

        Returns:
            Semantic analysis dictionary
        """
        logger.info(f"Analyzing semantics of {excel_path}")

        # Use first sheet if not specified
        if not sheet_name:
            sheet_name = structure_analysis.get('analyzed_sheet')

        # Read sample data (more rows than structure analysis)
        df_sample = self.excel_reader.read_excel_preview(excel_path, sheet_name, max_rows=100)
        data_sample = self.excel_reader.dataframe_to_text(df_sample)

        # Load prompt template
        with open('analyzer/prompts/semantic_analysis.txt', 'r') as f:
            prompt_template = f.read()

        # Build prompt
        prompt = prompt_template.format(
            structure_analysis=str(structure_analysis),
            data_sample=data_sample
        )

        # Get LLM analysis
        logger.info("Sending semantic analysis request to LLM...")
        analysis = self.llm.generate_json(
            prompt,
            system_prompt="You are an expert business data analyst. Extract semantic meaning and business context."
        )

        logger.info(f"Semantic analysis complete. Confidence: {analysis.get('confidence_score', 'N/A')}")

        return analysis
