"""Structure analyzer using LLM to understand Excel layout."""

import logging
from typing import Dict
from core.llm_client import LLMClient
from utils.excel_reader import ExcelReader
from utils.helpers import save_json

logger = logging.getLogger(__name__)


class StructureAnalyzer:
    """Analyzes Excel file structure using LLM."""

    def __init__(self, llm_client: LLMClient, sample_rows: int = 50):
        """
        Initialize structure analyzer.

        Args:
            llm_client: LLM client for AI analysis
            sample_rows: Number of rows to analyze
        """
        self.llm = llm_client
        self.sample_rows = sample_rows
        self.excel_reader = ExcelReader()

    def analyze(self, excel_path: str, sheet_name: str = None) -> Dict:
        """
        Analyze Excel file structure.

        Args:
            excel_path: Path to Excel file
            sheet_name: Sheet to analyze (None for first sheet)

        Returns:
            Structure analysis dictionary
        """
        logger.info(f"Analyzing structure of {excel_path}")

        # Get Excel file info
        excel_info = self.excel_reader.get_excel_info(excel_path)

        # Use first sheet if not specified
        if not sheet_name:
            sheet_name = excel_info['sheets'][0]['name']

        # Read preview
        df_preview = self.excel_reader.read_excel_preview(
            excel_path,
            sheet_name=sheet_name,
            max_rows=self.sample_rows
        )

        # Convert to text for LLM
        excel_preview = self.excel_reader.dataframe_to_text(df_preview)

        # Load prompt template
        with open('analyzer/prompts/structure_analysis.txt', 'r') as f:
            prompt_template = f.read()

        # Build prompt
        prompt = prompt_template.format(
            excel_info=str(excel_info),
            sample_rows=self.sample_rows,
            sheet_name=sheet_name,
            excel_preview=excel_preview
        )

        # Get LLM analysis
        logger.info("Sending structure analysis request to LLM...")
        analysis = self.llm.generate_json(
            prompt,
            system_prompt="You are an expert Excel data analyst. Provide detailed, accurate structural analysis."
        )

        # Add metadata
        analysis['analyzed_file'] = excel_path
        analysis['analyzed_sheet'] = sheet_name
        analysis['sample_rows'] = self.sample_rows

        logger.info(f"Structure analysis complete. Confidence: {analysis.get('confidence_score', 'N/A')}")

        return analysis
