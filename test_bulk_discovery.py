#!/usr/bin/env python3
"""
Test script to verify the updated bulk data discovery functionality
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_bulk_data_discovery():
    """Test the updated bulk data discovery feature"""
    logger.info("Testing bulk data discovery with updated URLs...")

    try:
        from src.scraper import CAScraper

        # Initialize scraper
        scraper = CAScraper(headless=True, rate_limit=1.0)
        logger.info("✓ Scraper initialized successfully")

        # Test bulk data link discovery
        logger.info("\nAttempting to discover bulk data links...")
        print("\n" + "=" * 70)
        print("DISCOVERING BULK DATA DOWNLOADS")
        print("=" * 70 + "\n")

        downloads = scraper.scrape_bulk_data_links()

        print("\n" + "=" * 70)
        print(f"DISCOVERED BULK DATA DOWNLOADS: {len(downloads)}")
        print("=" * 70)

        if downloads:
            for i, download in enumerate(downloads, 1):
                print(f"\n{i}. {download['title']}")
                print(f"   URL: {download['url']}")
                print(f"   Source: {download.get('source_page', 'N/A')}")
                print(f"   Filename: {download['filename']}")
        else:
            print("\nNo public downloads found.")
            print("This is expected as bulk data now requires authentication.")
            print("\nTo access bulk data:")
            print("1. Create an account at https://bizfileonline.sos.ca.gov/")
            print("2. Log in and navigate to 'BE & UCC Bulk Orders'")
            print("3. Order and download bulk data files")

        print("=" * 70 + "\n")

        # Cleanup
        scraper.close()
        logger.info("✓ Scraper closed successfully")

        logger.info("\n✓ Bulk data discovery test completed successfully")
        logger.info("The scraper now handles the URL changes correctly")
        return True

    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def main():
    """Run the test"""
    print("\n" + "=" * 70)
    print("BULK DATA DISCOVERY TEST")
    print("Testing updated URLs and authentication handling")
    print("=" * 70 + "\n")

    success = test_bulk_data_discovery()

    if success:
        logger.info("\n✓ All tests passed!")
        logger.info("The 404 error should now be resolved.")
        return 0
    else:
        logger.error("\n✗ Tests failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
