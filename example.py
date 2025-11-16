#!/usr/bin/env python3
"""
Example usage of the Business Data Extraction Tool
This script demonstrates how to use the tool programmatically
"""

import logging
from pathlib import Path
from src.extractor import DataExtractor
from src.filters import DataFilter
from src.validator import DataValidator


def example_basic_extraction():
    """
    Example 1: Basic extraction from a local CSV file
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Data Extraction")
    print("=" * 70)

    # Initialize extractor
    extractor = DataExtractor(input_dir="./input", output_dir="./output")

    # Read CSV file
    df = extractor.read_csv(Path("./input/sample_data.csv"))

    # Print info
    info = extractor.get_data_info(df)
    print(f"\nTotal records: {info['total_records']}")
    print(f"Columns: {', '.join(info['columns'])}")

    # Export to different formats
    extractor.export_data(df, "sample_output", format="csv")
    print("\nData exported to output/sample_output.csv")


def example_with_filters():
    """
    Example 2: Extraction with filtering
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Data Extraction with Filters")
    print("=" * 70)

    # Initialize components
    extractor = DataExtractor()

    # Read data
    df = extractor.read_csv(Path("./input/sample_data.csv"))
    print(f"\nOriginal records: {len(df)}")

    # Define filter configuration
    filter_config = {
        'filters': {
            'entity_types': {
                'enabled': True,
                'values': ['DOMESTIC LIMITED LIABILITY COMPANY', 'DOMESTIC STOCK']
            },
            'status': {
                'enabled': True,
                'values': ['ACTIVE']
            }
        },
        'output': {
            'max_records': 1000
        }
    }

    # Apply filters
    data_filter = DataFilter(filter_config)
    filtered_df = data_filter.apply_filters(df)
    filtered_df = data_filter.apply_output_limits(filtered_df)

    print(f"Filtered records: {len(filtered_df)}")

    # Export filtered data
    extractor.export_data(filtered_df, "filtered_output", format="csv")
    print("\nFiltered data exported to output/filtered_output.csv")


def example_with_validation():
    """
    Example 3: Extraction with data validation
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Data Extraction with Validation")
    print("=" * 70)

    # Initialize components
    extractor = DataExtractor()
    validator = DataValidator()

    # Read data
    df = extractor.read_csv(Path("./input/sample_data.csv"))

    # Validate data
    is_valid, report = validator.validate(df)

    # Print validation report
    print("\n" + validator.get_validation_report())

    if is_valid:
        print("\n✓ Data validation passed - proceeding with export")
        extractor.export_data(df, "validated_output", format="csv")
    else:
        print("\n✗ Data validation failed - please review issues")


def example_download_and_process():
    """
    Example 4: Download bulk data and process
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Download and Process Bulk Data")
    print("=" * 70)

    # Initialize extractor
    extractor = DataExtractor()

    # Download bulk data (example URL - replace with actual URL)
    bulk_url = "https://example.com/ca-sos-bulk-data.zip"

    try:
        # Download file
        downloaded_file = extractor.download_bulk_data(bulk_url)

        # Extract if ZIP
        if downloaded_file.suffix.lower() == '.zip':
            extracted_files = extractor.extract_zip(downloaded_file)
            csv_files = [f for f in extracted_files if f.suffix.lower() == '.csv']

            # Read all CSV files
            df = extractor.read_multiple_csvs(csv_files)
        else:
            df = extractor.read_csv(downloaded_file)

        print(f"\nProcessed {len(df)} records")

        # Apply filters and export
        # ... (filter logic here)

    except Exception as e:
        print(f"\nNote: This is a demonstration. Actual URL would be needed.")
        print(f"Error: {e}")


def example_custom_filtering():
    """
    Example 5: Custom filtering logic
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Custom Filtering")
    print("=" * 70)

    # Initialize extractor
    extractor = DataExtractor()

    # Read data
    df = extractor.read_csv(Path("./input/sample_data.csv"))

    # Custom filtering with pandas
    # Example: Filter businesses registered in San Francisco in 2024
    custom_filtered = df[
        (df['CITY'] == 'San Francisco') &
        (df['REGISTRATION_DATE'] >= '2024-01-01')
    ]

    print(f"\nOriginal records: {len(df)}")
    print(f"Custom filtered: {len(custom_filtered)}")

    # Export
    extractor.export_data(custom_filtered, "custom_filtered", format="json")
    print("\nCustom filtered data exported to output/custom_filtered.json")


def main():
    """Run all examples"""

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("BUSINESS DATA EXTRACTION TOOL - EXAMPLES")
    print("=" * 70)

    # Note: These examples assume you have sample data in ./input/sample_data.csv
    # For demonstration purposes, we'll show what each example does

    print("\nNote: These examples demonstrate the tool's capabilities.")
    print("To run them, you'll need sample data in ./input/sample_data.csv")
    print("\nYou can:")
    print("1. Place a CSV file from CA SOS in ./input/")
    print("2. Or uncomment the examples below to test with your data")

    # Uncomment to run examples:
    # example_basic_extraction()
    # example_with_filters()
    # example_with_validation()
    # example_download_and_process()
    # example_custom_filtering()

    print("\n" + "=" * 70)
    print("For CLI usage, run:")
    print("python -m src.cli --input your_data.csv --config config/filters.yaml")
    print("=" * 70)


if __name__ == '__main__':
    main()
