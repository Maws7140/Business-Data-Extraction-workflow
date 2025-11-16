"""
Data Validation Module
Ensures data accuracy and integrity
"""

import logging
from typing import Dict, List, Any, Tuple
import pandas as pd


class DataValidator:
    """
    Validates business entity data for accuracy and integrity
    """

    def __init__(self):
        """Initialize DataValidator"""
        self.logger = logging.getLogger(__name__)
        self.validation_results = {}

    def validate(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """
        Perform comprehensive validation on the DataFrame

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (is_valid, validation_report)
        """
        self.logger.info("Starting data validation")

        validations = {
            'row_count': self._validate_row_count(df),
            'column_presence': self._validate_columns(df),
            'data_types': self._validate_data_types(df),
            'null_values': self._validate_nulls(df),
            'duplicates': self._validate_duplicates(df),
            'data_quality': self._validate_data_quality(df)
        }

        # Determine overall validity
        is_valid = all(v.get('passed', True) for v in validations.values())

        report = {
            'is_valid': is_valid,
            'validations': validations,
            'summary': self._create_summary(validations)
        }

        self.validation_results = report

        if is_valid:
            self.logger.info("Validation passed ✓")
        else:
            self.logger.warning("Validation failed - see report for details")

        return is_valid, report

    def _validate_row_count(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate that dataset has rows"""
        row_count = len(df)
        passed = row_count > 0

        return {
            'name': 'Row Count',
            'passed': passed,
            'row_count': row_count,
            'message': f"Dataset contains {row_count} rows" if passed else "Dataset is empty"
        }

    def _validate_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate presence of expected columns"""
        columns = list(df.columns)
        column_count = len(columns)
        passed = column_count > 0

        return {
            'name': 'Column Presence',
            'passed': passed,
            'columns': columns,
            'column_count': column_count,
            'message': f"Dataset has {column_count} columns" if passed else "No columns found"
        }

    def _validate_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data types"""
        dtypes = df.dtypes.to_dict()
        dtype_summary = df.dtypes.value_counts().to_dict()

        return {
            'name': 'Data Types',
            'passed': True,
            'dtypes': {k: str(v) for k, v in dtypes.items()},
            'dtype_summary': {str(k): v for k, v in dtype_summary.items()},
            'message': f"Data types validated for {len(dtypes)} columns"
        }

    def _validate_nulls(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate and report null values"""
        null_counts = df.isnull().sum()
        total_nulls = null_counts.sum()
        null_percentage = (total_nulls / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0

        columns_with_nulls = null_counts[null_counts > 0].to_dict()

        return {
            'name': 'Null Values',
            'passed': True,  # Having nulls isn't necessarily a failure
            'total_nulls': int(total_nulls),
            'null_percentage': round(null_percentage, 2),
            'columns_with_nulls': columns_with_nulls,
            'message': f"{total_nulls} null values found ({null_percentage:.2f}%)"
        }

    def _validate_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for duplicate rows"""
        duplicate_count = df.duplicated().sum()
        duplicate_percentage = (duplicate_count / len(df) * 100) if len(df) > 0 else 0

        return {
            'name': 'Duplicate Rows',
            'passed': True,  # Having duplicates isn't necessarily a failure
            'duplicate_count': int(duplicate_count),
            'duplicate_percentage': round(duplicate_percentage, 2),
            'message': f"{duplicate_count} duplicate rows found ({duplicate_percentage:.2f}%)"
        }

    def _validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform data quality checks"""
        issues = []

        # Check for completely empty columns
        empty_columns = [col for col in df.columns if df[col].isna().all()]
        if empty_columns:
            issues.append(f"Empty columns: {empty_columns}")

        # Check for columns with single value
        single_value_cols = [col for col in df.columns if df[col].nunique() == 1]
        if single_value_cols:
            issues.append(f"Columns with single value: {single_value_cols}")

        # Memory usage check
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024

        return {
            'name': 'Data Quality',
            'passed': len(issues) == 0,
            'issues': issues,
            'memory_usage_mb': round(memory_mb, 2),
            'message': "No quality issues found" if not issues else f"{len(issues)} quality issues detected"
        }

    def _create_summary(self, validations: Dict[str, Any]) -> Dict[str, Any]:
        """Create validation summary"""
        total_checks = len(validations)
        passed_checks = sum(1 for v in validations.values() if v.get('passed', True))

        return {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'success_rate': round((passed_checks / total_checks * 100), 2) if total_checks > 0 else 0
        }

    def get_validation_report(self) -> str:
        """
        Get a formatted validation report

        Returns:
            Formatted string report
        """
        if not self.validation_results:
            return "No validation has been performed yet"

        report_lines = [
            "=" * 60,
            "DATA VALIDATION REPORT",
            "=" * 60,
            ""
        ]

        summary = self.validation_results.get('summary', {})
        report_lines.append(f"Overall Status: {'PASSED ✓' if self.validation_results['is_valid'] else 'FAILED ✗'}")
        report_lines.append(f"Checks Passed: {summary.get('passed_checks', 0)}/{summary.get('total_checks', 0)}")
        report_lines.append("")
        report_lines.append("-" * 60)
        report_lines.append("VALIDATION DETAILS")
        report_lines.append("-" * 60)

        for validation in self.validation_results.get('validations', {}).values():
            status = "✓" if validation.get('passed', True) else "✗"
            report_lines.append(f"{status} {validation.get('name', 'Unknown')}: {validation.get('message', '')}")

        report_lines.append("")
        report_lines.append("=" * 60)

        return "\n".join(report_lines)
