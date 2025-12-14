"""Execute generated transformation code."""

import logging
import sys
import os
import pandas as pd
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class CodeRunner:
    """Executes generated transformation code safely."""

    def __init__(self):
        """Initialize code runner."""
        pass

    def execute(self, code_path: str, source_path: str, output_path: str) -> Tuple[bool, Optional[pd.DataFrame], str]:
        """
        Execute transformation code.

        Args:
            code_path: Path to generated Python code
            source_path: Path to source Excel
            output_path: Path for output file

        Returns:
            Tuple of (success, result_dataframe, error_message)
        """
        logger.info(f"Executing transformation code: {code_path}")

        try:
            # Create a namespace for execution
            namespace = {
                '__name__': '__main__',
                '__file__': code_path,
                'pd': pd,
                'pandas': pd,
                'numpy': __import__('numpy'),
            }

            # Read and execute the code
            with open(code_path, 'r') as f:
                code = f.read()

            exec(code, namespace)

            # Call the main function
            if 'main' not in namespace:
                raise ValueError("Generated code does not contain a main() function")

            logger.info("Calling main() function...")
            result_df = namespace['main'](source_path, output_path)

            if not isinstance(result_df, pd.DataFrame):
                raise ValueError("main() function did not return a DataFrame")

            logger.info(f"Execution successful. Result shape: {result_df.shape}")
            return True, result_df, ""

        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.debug(traceback.format_exc())
            return False, None, error_msg

    def validate_code(self, code_path: str) -> Tuple[bool, str]:
        """
        Validate that code is syntactically correct.

        Args:
            code_path: Path to code file

        Returns:
            Tuple of (valid, error_message)
        """
        try:
            with open(code_path, 'r') as f:
                code = f.read()

            compile(code, code_path, 'exec')
            return True, ""

        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"
