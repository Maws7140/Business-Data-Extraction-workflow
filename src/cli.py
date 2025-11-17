"""
Command Line Interface for Business Data Extraction Tool
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional
import yaml
from dotenv import load_dotenv

from .extractor import DataExtractor
from .filters import DataFilter
from .validator import DataValidator
from .scraper import BusinessDataScraper


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )


def load_filter_config(config_path: str) -> dict:
    """
    Load filter configuration from YAML file

    Args:
        config_path: Path to YAML config file

    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def main():
    """Main CLI entry point"""

    parser = argparse.ArgumentParser(
        description='California Secretary of State Business Data Extraction Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from local CSV file with filters
  python -m src.cli --input data.csv --config config/filters.yaml --output results

  # Download and process bulk data
  python -m src.cli --download-url https://example.com/data.zip --config config/filters.yaml

  # Process multiple CSV files
  python -m src.cli --input-dir ./data --config config/filters.yaml --output results
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input',
        type=str,
        help='Input CSV file path'
    )
    input_group.add_argument(
        '--input-dir',
        type=str,
        help='Directory containing CSV files'
    )
    input_group.add_argument(
        '--download-url',
        type=str,
        help='URL to download bulk data'
    )
    input_group.add_argument(
        '--scrape',
        action='store_true',
        help='Scrape data from CA SOS website'
    )
    input_group.add_argument(
        '--discover-bulk',
        action='store_true',
        help='Discover and list bulk data download links'
    )

    # Configuration
    parser.add_argument(
        '--config',
        type=str,
        default='config/filters.yaml',
        help='Path to filter configuration YAML file (default: config/filters.yaml)'
    )

    # Output options
    parser.add_argument(
        '--output',
        type=str,
        default='output/filtered_data',
        help='Output filename (without extension, default: output/filtered_data)'
    )
    parser.add_argument(
        '--output-format',
        type=str,
        choices=['csv', 'json', 'excel'],
        default='csv',
        help='Output format (default: csv)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory (default: output)'
    )

    # Processing options
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip data validation step'
    )
    parser.add_argument(
        '--validation-report',
        type=str,
        help='Save validation report to file'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        help='Chunk size for reading large CSV files'
    )
    parser.add_argument(
        '--encoding',
        type=str,
        default='utf-8',
        help='File encoding (default: utf-8)'
    )

    # Scraper options
    parser.add_argument(
        '--business-names',
        type=str,
        nargs='+',
        help='Business names to scrape (space-separated list)'
    )
    parser.add_argument(
        '--entity-numbers',
        type=str,
        nargs='+',
        help='Entity numbers to scrape (space-separated list)'
    )
    parser.add_argument(
        '--scrape-config',
        type=str,
        help='Path to scraper configuration YAML file'
    )
    parser.add_argument(
        '--max-scrape-results',
        type=int,
        default=100,
        help='Maximum results per scrape search (default: 100)'
    )
    parser.add_argument(
        '--download-bulk-data',
        action='store_true',
        help='Download discovered bulk data files (use with --discover-bulk)'
    )

    # Logging
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log file path'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)

    logger.info("=" * 70)
    logger.info("Business Data Extraction Tool - Starting")
    logger.info("=" * 70)

    try:
        # Initialize extractor
        extractor = DataExtractor(
            input_dir=os.getenv('DATA_INPUT_DIR', './input'),
            output_dir=args.output_dir
        )

        # Handle special scraping modes
        if args.discover_bulk:
            logger.info("\n[Discover Mode] Finding bulk data downloads...")
            scraper = BusinessDataScraper(output_dir=args.output_dir)

            try:
                downloads = scraper.discover_bulk_downloads(
                    download_all=args.download_bulk_data,
                    output_dir=Path(args.output_dir) / "bulk_downloads"
                )

                print("\n" + "=" * 70)
                print("DISCOVERED BULK DATA DOWNLOADS")
                print("=" * 70)

                for i, download in enumerate(downloads, 1):
                    print(f"\n{i}. {download['title']}")
                    print(f"   URL: {download['url']}")
                    print(f"   Filename: {download['filename']}")
                    if download.get('downloaded'):
                        print(f"   Downloaded to: {download['local_path']}")

                print("\n" + "=" * 70)

            finally:
                scraper.close()

            return

        # Step 1: Load data
        logger.info("\n[Step 1/4] Loading data...")

        if args.scrape:
            # Scrape data from CA SOS website
            logger.info("Scraping data from CA SOS website...")

            scraper = BusinessDataScraper(output_dir=args.output_dir)

            try:
                # Load scrape config if provided
                if args.scrape_config:
                    with open(args.scrape_config, 'r') as f:
                        scrape_config = yaml.safe_load(f)
                else:
                    # Use CLI arguments
                    scrape_config = {
                        'business_names': args.business_names,
                        'entity_numbers': args.entity_numbers,
                        'max_results': args.max_scrape_results
                    }

                if not scrape_config.get('business_names') and not scrape_config.get('entity_numbers'):
                    logger.error("No business names or entity numbers provided for scraping")
                    logger.error("Use --business-names or --entity-numbers or --scrape-config")
                    sys.exit(1)

                # Scrape and save data
                df, scraped_path = scraper.scrape_and_save(scrape_config)

                if df.empty:
                    logger.warning("No data scraped. Exiting.")
                    sys.exit(0)

                logger.info(f"Scraped {len(df)} records")

            finally:
                scraper.close()

        elif args.download_url:
            # Download and extract
            downloaded_file = extractor.download_bulk_data(args.download_url)

            if downloaded_file.suffix.lower() == '.zip':
                extracted_files = extractor.extract_zip(downloaded_file)
                csv_files = [f for f in extracted_files if f.suffix.lower() == '.csv']
                df = extractor.read_multiple_csvs(csv_files, encoding=args.encoding)
            else:
                df = extractor.read_csv(downloaded_file, encoding=args.encoding, chunk_size=args.chunk_size)

        elif args.input:
            # Single file
            input_path = Path(args.input)
            if input_path.suffix.lower() == '.zip':
                extracted_files = extractor.extract_zip(input_path)
                csv_files = [f for f in extracted_files if f.suffix.lower() == '.csv']
                df = extractor.read_multiple_csvs(csv_files, encoding=args.encoding)
            else:
                df = extractor.read_csv(input_path, encoding=args.encoding, chunk_size=args.chunk_size)

        elif args.input_dir:
            # Multiple files
            input_dir = Path(args.input_dir)
            csv_files = list(input_dir.glob('*.csv'))
            df = extractor.read_multiple_csvs(csv_files, encoding=args.encoding)

        logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
        logger.info(f"Columns: {', '.join(df.columns)}")

        # Step 2: Validate data
        if not args.skip_validation:
            logger.info("\n[Step 2/4] Validating data...")
            validator = DataValidator()
            is_valid, validation_report = validator.validate(df)

            print("\n" + validator.get_validation_report())

            if args.validation_report:
                report_path = Path(args.validation_report)
                report_path.parent.mkdir(parents=True, exist_ok=True)
                with open(report_path, 'w') as f:
                    f.write(validator.get_validation_report())
                logger.info(f"Validation report saved to {report_path}")

            if not is_valid:
                logger.warning("Data validation found issues - proceeding with caution")
        else:
            logger.info("\n[Step 2/4] Skipping validation (--skip-validation flag set)")

        # Step 3: Filter data
        logger.info("\n[Step 3/4] Applying filters...")
        filter_config = load_filter_config(args.config)
        data_filter = DataFilter(filter_config)

        filtered_df = data_filter.apply_filters(df)
        filtered_df = data_filter.apply_output_limits(filtered_df)

        logger.info(f"Filtered to {len(filtered_df)} records")

        # Step 4: Export data
        logger.info("\n[Step 4/4] Exporting data...")

        # Use output format from config if not specified in CLI
        output_format = args.output_format
        if output_format == 'csv' and filter_config.get('output', {}).get('format'):
            output_format = filter_config['output']['format']

        # Extract filename from output path
        output_path = Path(args.output)
        filename = output_path.stem

        exported_file = extractor.export_data(
            filtered_df,
            filename=filename,
            format=output_format,
            include_index=False
        )

        logger.info(f"\nSuccess! Exported to {exported_file}")

        # Print summary
        print("\n" + "=" * 70)
        print("EXTRACTION SUMMARY")
        print("=" * 70)
        print(f"Input records:     {len(df):,}")
        print(f"Output records:    {len(filtered_df):,}")
        print(f"Records removed:   {len(df) - len(filtered_df):,}")
        print(f"Retention rate:    {(len(filtered_df) / len(df) * 100):.2f}%")
        print(f"Output file:       {exported_file}")
        print(f"Output format:     {output_format}")
        print("=" * 70)

        logger.info("\nData extraction completed successfully!")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during extraction: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
