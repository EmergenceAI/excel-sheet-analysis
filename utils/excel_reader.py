"""Excel file reading utilities."""

import pandas as pd
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ExcelReader:
    """Utility class for reading and analyzing Excel files."""

    @staticmethod
    def read_excel_preview(file_path: str, sheet_name: Optional[str] = None,
                          max_rows: int = 50) -> pd.DataFrame:
        """
        Read a preview of an Excel file.

        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name to read (None for first sheet)
            max_rows: Maximum rows to read

        Returns:
            DataFrame with preview data
        """
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=max_rows)
            else:
                df = pd.read_excel(file_path, header=None, nrows=max_rows)

            logger.info(f"Read {len(df)} rows from {file_path}")
            return df
        except Exception as e:
            logger.error(f"Failed to read Excel file: {e}")
            raise

    @staticmethod
    def get_sheet_names(file_path: str) -> List[str]:
        """
        Get list of sheet names from Excel file.

        Args:
            file_path: Path to Excel file

        Returns:
            List of sheet names
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            logger.error(f"Failed to get sheet names: {e}")
            raise

    @staticmethod
    def dataframe_to_text(df: pd.DataFrame, max_width: int = 50) -> str:
        """
        Convert DataFrame to text representation for LLM.

        Args:
            df: DataFrame to convert
            max_width: Maximum column width

        Returns:
            Text representation of DataFrame
        """
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', max_width)

        return df.to_string()

    @staticmethod
    def get_excel_info(file_path: str) -> Dict:
        """
        Get basic information about an Excel file.

        Args:
            file_path: Path to Excel file

        Returns:
            Dictionary with file info
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names

            info = {
                "file_path": file_path,
                "sheet_count": len(sheets),
                "sheets": []
            }

            for sheet in sheets:
                df = pd.read_excel(file_path, sheet_name=sheet, header=None, nrows=0)
                # Read one more time to get actual shape
                df_full = pd.read_excel(file_path, sheet_name=sheet, header=None)

                info["sheets"].append({
                    "name": sheet,
                    "rows": len(df_full),
                    "columns": len(df_full.columns)
                })

            return info
        except Exception as e:
            logger.error(f"Failed to get Excel info: {e}")
            raise
