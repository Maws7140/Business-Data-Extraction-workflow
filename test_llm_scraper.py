#!/usr/bin/env python3
"""
Test and example script for LLM-based scraper
Demonstrates how to use the new LLM scraper for extracting business data
"""

import sys
import logging
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_imports():
    """Test that LLM scraper can be imported"""
    logger.info("Testing LLM scraper imports...")

    try:
        from src.llm_scraper import LLMScraper, BusinessLLMScraper
        logger.info("✓ Successfully imported LLM scraper modules")
        return True
    except ImportError as e:
        logger.error(f"✗ Failed to import LLM scraper: {e}")
        logger.info("Make sure to install dependencies: pip install -r requirements.txt")
        return False


def test_initialization():
    """Test LLM scraper initialization"""
    logger.info("Testing LLM scraper initialization...")

    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("⚠ ANTHROPIC_API_KEY not set in environment")
        logger.info("Set it with: export ANTHROPIC_API_KEY='your-api-key'")
        return False

    try:
        from src.llm_scraper import LLMScraper, BusinessLLMScraper

        # Test LLMScraper
        scraper1 = LLMScraper(api_key=api_key)
        logger.info("✓ LLMScraper initialized successfully")

        # Test BusinessLLMScraper
        scraper2 = BusinessLLMScraper(api_key=api_key, output_dir="./test_output")
        logger.info("✓ BusinessLLMScraper initialized successfully")

        # Cleanup
        scraper1.close()
        scraper2.close()

        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize scraper: {e}")
        return False


def test_basic_scraping():
    """Test basic web scraping functionality"""
    logger.info("Testing basic scraping...")

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("⚠ Skipping - ANTHROPIC_API_KEY not set")
        return False

    try:
        from src.llm_scraper import LLMScraper

        scraper = LLMScraper(api_key=api_key)

        # Test fetching a page
        test_url = "https://example.com"
        logger.info(f"Fetching {test_url}...")

        html = scraper.fetch_page(test_url)

        if html:
            logger.info(f"✓ Successfully fetched page ({len(html)} bytes)")

            # Test HTML to markdown conversion
            markdown = scraper.html_to_markdown(html, base_url=test_url)
            logger.info(f"✓ Converted to markdown ({len(markdown)} characters)")

            scraper.close()
            return True
        else:
            logger.error("✗ Failed to fetch page")
            scraper.close()
            return False

    except Exception as e:
        logger.error(f"✗ Scraping test failed: {e}")
        return False


def example_extract_business_data():
    """Example: Extract business data from a page"""
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE: Extracting Business Data")
    logger.info("="*70)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("⚠ ANTHROPIC_API_KEY not set. This example requires an API key.")
        logger.info("Set it with: export ANTHROPIC_API_KEY='your-api-key'")
        return

    try:
        from src.llm_scraper import BusinessLLMScraper

        scraper = BusinessLLMScraper(api_key=api_key)

        # Example: Scrape a business page
        # (Replace with actual business page URL)
        example_url = "https://example.com/business-page"

        logger.info(f"Scraping business data from: {example_url}")
        logger.info("NOTE: This is a demo URL. Replace with actual business page for real results.")

        # For demonstration, we'll show how to use the scraper
        logger.info("\nUsage example:")
        logger.info("  business_data = scraper.scrape_business(url)")
        logger.info("  print(business_data)")

        scraper.close()

    except Exception as e:
        logger.error(f"Example failed: {e}")


def example_bulk_download_discovery():
    """Example: Discover bulk download links"""
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE: Discovering Bulk Download Links")
    logger.info("="*70)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("⚠ ANTHROPIC_API_KEY not set")
        return

    try:
        from src.llm_scraper import BusinessLLMScraper

        scraper = BusinessLLMScraper(api_key=api_key)

        # Example URLs to check for bulk downloads
        example_urls = [
            "https://www.sos.ca.gov/business-programs/business-entities",
        ]

        for url in example_urls:
            logger.info(f"\nChecking {url} for download links...")

            try:
                downloads = scraper.discover_bulk_downloads(
                    url,
                    download_patterns=[r'\.(zip|csv|txt|xlsx)$']
                )

                if downloads:
                    logger.info(f"✓ Found {len(downloads)} download links:")
                    for dl in downloads[:5]:  # Show first 5
                        logger.info(f"  - {dl['text']}: {dl['url']}")
                else:
                    logger.info("  No download links found")

            except Exception as e:
                logger.warning(f"  Error: {e}")

        scraper.close()

    except Exception as e:
        logger.error(f"Example failed: {e}")


def show_usage_examples():
    """Show usage examples"""
    logger.info("\n" + "="*70)
    logger.info("LLM SCRAPER USAGE EXAMPLES")
    logger.info("="*70)

    usage = """
1. BASIC SCRAPING
   --------------------------------------------------
   from src.llm_scraper import LLMScraper

   scraper = LLMScraper(api_key='your-key')

   # Scrape a page with custom schema
   schema = {
       'company_name': 'Extract the company name',
       'address': 'Extract the full address',
       'phone': 'Extract phone number'
   }

   data = scraper.scrape_page(url, schema)
   print(data)

   scraper.close()


2. BUSINESS DATA SCRAPING
   --------------------------------------------------
   from src.llm_scraper import BusinessLLMScraper

   scraper = BusinessLLMScraper(api_key='your-key')

   # Scrape single business
   business = scraper.scrape_business(business_url)

   # Scrape multiple businesses
   urls = ['url1', 'url2', 'url3']
   df = scraper.scrape_businesses(urls)

   # Save to file
   df, path = scraper.scrape_and_save(urls)

   scraper.close()


3. DISCOVER DOWNLOAD LINKS
   --------------------------------------------------
   from src.llm_scraper import BusinessLLMScraper

   scraper = BusinessLLMScraper(api_key='your-key')

   # Find bulk data downloads
   downloads = scraper.discover_bulk_downloads(
       url='https://example.com/data',
       download_patterns=[r'\\.zip$', r'\\.csv$']
   )

   for dl in downloads:
       print(f"{dl['text']}: {dl['url']}")

   scraper.close()


4. CUSTOM EXTRACTION
   --------------------------------------------------
   from src.llm_scraper import LLMScraper

   scraper = LLMScraper(api_key='your-key')

   # Define custom schema with detailed config
   schema = {
       'title': {
           'type': 'string',
           'description': 'Page title',
           'required': True
       },
       'items': {
           'type': 'array',
           'description': 'List of all items found',
           'required': False
       }
   }

   # Extract with additional context
   data = scraper.scrape_page(
       url,
       schema,
       additional_context="Focus on product information"
   )

   scraper.close()


ENVIRONMENT SETUP
--------------------------------------------------
1. Install dependencies:
   pip install -r requirements.txt

2. Set API key:
   export ANTHROPIC_API_KEY='your-anthropic-api-key'

3. Run scraper:
   python your_script.py

"""

    print(usage)


def main():
    """Run all tests and examples"""
    print("\n" + "="*70)
    print("LLM SCRAPER TEST SUITE")
    print("="*70 + "\n")

    tests = [
        ("Import Test", test_imports),
        ("Initialization Test", test_initialization),
        ("Basic Scraping Test", test_basic_scraping),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        print("-"*70)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test crashed: {e}", exc_info=True)
            results.append((test_name, False))
        print()

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status:10} - {test_name}")

    print("-"*70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70 + "\n")

    # Run examples
    if passed > 0:
        example_extract_business_data()
        example_bulk_download_discovery()
        show_usage_examples()

    if passed == total:
        logger.info("All tests passed! The LLM scraper is ready to use.")
        return 0
    else:
        logger.warning(f"{total - passed} test(s) failed. Check errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
