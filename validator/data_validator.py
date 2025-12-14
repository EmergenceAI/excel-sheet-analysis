"""Validate generated data against ground truth."""

import logging
import pandas as pd
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates transformation output against ground truth."""

    def __init__(self, accuracy_threshold: float = 0.99):
        """
        Initialize data validator.

        Args:
            accuracy_threshold: Minimum accuracy required (0.0 to 1.0)
        """
        self.accuracy_threshold = accuracy_threshold

    def validate(self, generated_df: pd.DataFrame, ground_truth_path: str,
                 sample_size: int = None) -> Dict:
        """
        Validate generated data against ground truth.

        Args:
            generated_df: Generated DataFrame
            ground_truth_path: Path to ground truth Excel
            sample_size: Number of rows to compare (None for all)

        Returns:
            Validation report dictionary
        """
        logger.info("Validating generated data against ground truth...")

        # Load ground truth
        truth_df = pd.read_excel(ground_truth_path)

        # Schema validation
        schema_valid, schema_errors = self._validate_schema(generated_df, truth_df)

        if not schema_valid:
            return {
                "passed": False,
                "schema_match": False,
                "schema_errors": schema_errors,
                "value_accuracy": 0.0,
                "message": "Schema validation failed"
            }

        # Row count validation
        row_count_match = len(generated_df) == len(truth_df)

        # Value validation
        if sample_size and sample_size < len(truth_df):
            # Sample comparison
            sample_indices = truth_df.sample(n=sample_size, random_state=42).index
            truth_sample = truth_df.loc[sample_indices]
            gen_sample = generated_df.loc[sample_indices]
        else:
            # Full comparison
            truth_sample = truth_df
            gen_sample = generated_df

        accuracy, mismatches = self._compare_values(gen_sample, truth_sample)

        passed = schema_valid and row_count_match and (accuracy >= self.accuracy_threshold)

        report = {
            "passed": passed,
            "schema_match": schema_valid,
            "row_count_match": row_count_match,
            "rows_expected": len(truth_df),
            "rows_actual": len(generated_df),
            "value_accuracy": accuracy,
            "accuracy_threshold": self.accuracy_threshold,
            "mismatches_count": len(mismatches),
            "mismatches_sample": mismatches[:20],  # First 20 mismatches
            "summary": f"{'PASSED' if passed else 'FAILED'}: {accuracy*100:.2f}% accuracy, {len(mismatches)} mismatches"
        }

        logger.info(report['summary'])

        return report

    def _validate_schema(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate that schemas match."""
        errors = []

        # Check columns
        if list(df1.columns) != list(df2.columns):
            errors.append(f"Column mismatch. Expected: {list(df2.columns)}, Got: {list(df1.columns)}")

        # Check data types (lenient - allow int vs float)
        for col in df2.columns:
            if col not in df1.columns:
                continue

            expected_type = df2[col].dtype
            actual_type = df1[col].dtype

            # Numeric types are compatible
            if pd.api.types.is_numeric_dtype(expected_type) and pd.api.types.is_numeric_dtype(actual_type):
                continue

            if expected_type != actual_type:
                errors.append(f"Column '{col}' type mismatch. Expected: {expected_type}, Got: {actual_type}")

        return len(errors) == 0, errors

    def _compare_values(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[float, List[Dict]]:
        """Compare values between dataframes."""
        mismatches = []
        total_cells = df1.shape[0] * df1.shape[1]
        matching_cells = 0

        for idx in df1.index:
            for col in df1.columns:
                val1 = df1.loc[idx, col]
                val2 = df2.loc[idx, col]

                # Handle NaN
                if pd.isna(val1) and pd.isna(val2):
                    matching_cells += 1
                    continue

                # Compare values
                if self._values_match(val1, val2):
                    matching_cells += 1
                else:
                    mismatches.append({
                        "row": int(idx),
                        "column": col,
                        "expected": val2,
                        "actual": val1,
                        "difference": self._calculate_difference(val1, val2)
                    })

        accuracy = matching_cells / total_cells if total_cells > 0 else 0.0

        return accuracy, mismatches

    def _values_match(self, val1, val2, tolerance: float = 1e-6) -> bool:
        """Check if two values match (with tolerance for floats)."""
        # Type check
        if type(val1) != type(val2):
            # Allow int/float mismatch
            if not (isinstance(val1, (int, float)) and isinstance(val2, (int, float))):
                return False

        # Numeric comparison
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            return abs(val1 - val2) <= tolerance

        # String comparison
        return val1 == val2

    def _calculate_difference(self, val1, val2):
        """Calculate difference between values."""
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            return val1 - val2
        return None
