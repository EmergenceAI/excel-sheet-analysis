"""
Excel Sheet Analysis Tool
Analyze Excel spreadsheets and generate insights
"""

import argparse
import sys
from pathlib import Path
import pandas as pd


def analyze_excel(file_path: str) -> None:
    """
    Analyze an Excel file and display basic information.

    Args:
        file_path: Path to the Excel file
    """
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)

        print(f"\n{'='*50}")
        print(f"Excel File Analysis: {Path(file_path).name}")
        print(f"{'='*50}\n")

        # Display sheet information
        print(f"Number of sheets: {len(excel_file.sheet_names)}")
        print(f"Sheet names: {', '.join(excel_file.sheet_names)}\n")

        # Analyze each sheet
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            print(f"\n--- Sheet: {sheet_name} ---")
            print(f"Rows: {len(df)}")
            print(f"Columns: {len(df.columns)}")
            print(f"Column names: {', '.join(df.columns)}")

            # Display first few rows
            print(f"\nFirst 5 rows:")
            print(df.head())

            # Basic statistics
            print(f"\nBasic statistics:")
            print(df.describe())

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Analyze Excel spreadsheets and generate insights"
    )
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="Path to the Excel file to analyze"
    )

    args = parser.parse_args()
    analyze_excel(args.file)


if __name__ == "__main__":
    main()
