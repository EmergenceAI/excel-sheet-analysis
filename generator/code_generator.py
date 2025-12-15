"""Generate transformation code using LLM."""

import logging
import os
from typing import Dict
from core.llm_client import LLMClient
from generator.prompt_builder import PromptBuilder
from utils.helpers import get_timestamp, ensure_dir

logger = logging.getLogger(__name__)


class CodeGenerator:
    """Generates Python transformation code using LLM."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize code generator.

        Args:
            llm_client: LLM client for code generation
        """
        self.llm = llm_client
        self.prompt_builder = PromptBuilder()

    def generate(self, analysis_report: Dict, source_path: str,
                 ground_truth_path: str, output_dir: str = "generator/generated") -> str:
        """
        Generate transformation code.

        Args:
            analysis_report: Complete analysis report
            source_path: Path to source Excel
            ground_truth_path: Path to ground truth
            output_dir: Directory to save generated code

        Returns:
            Path to generated code file
        """
        logger.info("Generating transformation code...")

        # Build prompt
        prompt = self.prompt_builder.build_code_generation_prompt(
            analysis_report,
            source_path,
            ground_truth_path
        )

        # Generate code
        code = self.llm.generate(
            prompt,
            system_prompt="You are an expert Python programmer. Generate clean, efficient, production-ready code."
        )

        # Extract code from response (remove markdown if present)
        code = self._extract_code(code)

        # Save to file
        ensure_dir(output_dir)
        timestamp = get_timestamp()
        output_path = os.path.join(output_dir, f"transform_{timestamp}.py")

        with open(output_path, 'w') as f:
            f.write(code)

        logger.info(f"Generated transformation code saved to: {output_path}")

        return output_path

    def _extract_code(self, response: str) -> str:
        """
        Extract Python code from LLM response.

        Args:
            response: LLM response that may contain markdown

        Returns:
            Clean Python code
        """
        # If wrapped in markdown code blocks, extract
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0].strip()
        else:
            code = response.strip()

        return code
