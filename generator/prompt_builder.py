"""Build prompts for code generation."""

import logging
import pandas as pd
from typing import Dict

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds prompts for LLM code generation."""

    @staticmethod
    def build_code_generation_prompt(analysis_report: Dict, source_path: str,
                                     ground_truth_path: str) -> str:
        """
        Build comprehensive prompt for code generation.

        Args:
            analysis_report: Complete analysis report
            source_path: Path to source Excel
            ground_truth_path: Path to ground truth

        Returns:
            Complete prompt for code generation
        """
        structure = analysis_report['structure_analysis']
        semantic = analysis_report['semantic_analysis']
        transformation = analysis_report['transformation_plan']

        # Read samples for examples
        source_sample = pd.read_excel(source_path, header=None, nrows=20).to_string()
        truth_sample = pd.read_excel(ground_truth_path, nrows=20).to_string()

        prompt = f"""You are an expert Python developer specializing in data transformation with pandas.

Generate a COMPLETE, PRODUCTION-READY Python script to transform the messy source Excel file into the exact target format shown in the ground truth.

=== SOURCE ANALYSIS ===

STRUCTURE:
{str(structure)}

SEMANTICS:
{str(semantic)}

TRANSFORMATION PLAN:
{str(transformation)}

=== SOURCE DATA SAMPLE ===
{source_sample}

=== TARGET DATA (GROUND TRUTH) ===
Columns: {transformation['target_columns']}
{truth_sample}

=== REQUIREMENTS ===

1. Generate a complete, standalone Python script
2. Include all necessary imports (pandas, numpy, etc.)
3. Implement helper functions for each major transformation step
4. Add comprehensive error handling and logging
5. Include validation checks to ensure output matches target schema
6. Add docstrings to all functions
7. Make the code modular and well-organized
8. The final output must match the target schema EXACTLY:
   - Same column names in same order
   - Same data types
   - Same row structure

9. Include a main() function that:
   - Takes input_path and output_path as parameters
   - Performs all transformations
   - Validates the result
   - Saves the cleaned data
   - Returns the final DataFrame

10. Add inline comments explaining complex logic

=== OUTPUT FORMAT ===

Return ONLY the Python code, ready to execute. Start with imports, define functions, then main().

The script should be executable as:
```python
df_result = main("source.xlsx", "output.csv")
```

Generate the complete transformation code now:
"""

        return prompt
