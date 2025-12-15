"""Optimize generated code based on validation failures."""

import logging
import os
from typing import Dict
from core.llm_client import LLMClient
from utils.helpers import get_timestamp, ensure_dir

logger = logging.getLogger(__name__)


class CodeOptimizer:
    """Optimizes transformation code using LLM."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize code optimizer.

        Args:
            llm_client: LLM client for optimization
        """
        self.llm = llm_client

    def optimize(self, code_path: str, validation_report: Dict,
                 output_dir: str = "generator/generated") -> str:
        """
        Optimize code based on validation failures.

        Args:
            code_path: Path to current code
            validation_report: Validation results
            output_dir: Directory to save optimized code

        Returns:
            Path to optimized code
        """
        logger.info("Optimizing transformation code...")

        # Read current code
        with open(code_path, 'r') as f:
            current_code = f.read()

        # Prepare mismatch examples
        mismatches = validation_report.get('mismatches_sample', [])
        mismatch_examples = "\n".join([
            f"Row {m['row']}, Column '{m['column']}': Expected {m['expected']}, Got {m['actual']}"
            for m in mismatches[:10]
        ])

        # Load prompt template
        with open('optimizer/prompts/debug_and_fix.txt', 'r') as f:
            prompt_template = f.read()

        # Build prompt
        prompt = prompt_template.format(
            current_code=current_code,
            validation_report=str(validation_report),
            mismatch_examples=mismatch_examples
        )

        # Generate optimized code
        optimized_code = self.llm.generate(
            prompt,
            system_prompt="You are an expert debugger and Python programmer. Fix code issues precisely."
        )

        # Extract code
        optimized_code = self._extract_code(optimized_code)

        # Save to new file
        ensure_dir(output_dir)
        timestamp = get_timestamp()
        output_path = os.path.join(output_dir, f"transform_{timestamp}_optimized.py")

        with open(output_path, 'w') as f:
            f.write(optimized_code)

        logger.info(f"Optimized code saved to: {output_path}")

        return output_path

    def _extract_code(self, response: str) -> str:
        """Extract Python code from LLM response."""
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0].strip()
        else:
            code = response.strip()

        return code
