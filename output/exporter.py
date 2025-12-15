"""Export cleaned data to various formats."""

import logging
import pandas as pd
import sqlite3
import os
from typing import List
from utils.helpers import ensure_dir

logger = logging.getLogger(__name__)


class DataExporter:
    """Exports cleaned data to multiple formats."""

    def export(self, df: pd.DataFrame, base_path: str, formats: List[str]) -> List[str]:
        """
        Export DataFrame to specified formats.

        Args:
            df: DataFrame to export
            base_path: Base path for output files (without extension)
            formats: List of formats ('csv', 'excel', 'sqlite', 'json')

        Returns:
            List of paths to exported files
        """
        exported_files = []

        # Ensure output directory exists
        ensure_dir(os.path.dirname(base_path))

        # CSV
        if 'csv' in formats:
            csv_path = f"{base_path}.csv"
            df.to_csv(csv_path, index=False)
            logger.info(f"Exported to CSV: {csv_path}")
            exported_files.append(csv_path)

        # Excel
        if 'excel' in formats:
            excel_path = f"{base_path}.xlsx"
            df.to_excel(excel_path, index=False)
            logger.info(f"Exported to Excel: {excel_path}")
            exported_files.append(excel_path)

        # SQLite
        if 'sqlite' in formats:
            db_path = f"{base_path}.db"
            conn = sqlite3.connect(db_path)
            table_name = os.path.basename(base_path).replace('-', '_')
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.close()
            logger.info(f"Exported to SQLite: {db_path} (table: {table_name})")
            exported_files.append(db_path)

        # JSON
        if 'json' in formats:
            json_path = f"{base_path}.json"
            df.to_json(json_path, orient='records', indent=2)
            logger.info(f"Exported to JSON: {json_path}")
            exported_files.append(json_path)

        return exported_files
