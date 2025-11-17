#!/usr/bin/env python3
"""
Example: Using LLM Scraper for Business Data Extraction
This demonstrates how to use the new LLM-based scraper instead of Selenium
"""

import os
import logging
from pathlib import Path
from src.llm_scraper import BusinessLLMScraper, LLMScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_1_scrape_single_business():
    """Example 1: Scrape a single business page"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Scrape Single Business Page")
    print("="*70 + "\n")

    # Initialize scraper
    scraper = BusinessLLMScraper()

    # Example business page URL
    # Replace with actual business page from CA SOS or other source
    business_url = "https://bizfileonline.sos.ca.gov/search/business"

    logger.info(f"Scraping business data from: {business_url}")

    try:
        # Scrape the business page
        business_data = scraper.scrape_business(business_url)

        if business_data:
            logger.info("Successfully extracted business data:")
            for key, value in business_data.items():
                if not key.startswith('_'):
                    logger.info(f"  {key}: {value}")
        else:
            logger.warning("No data extracted")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        scraper.close()


def example_2_scrape_multiple_businesses():
    """Example 2: Scrape multiple business pages"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Scrape Multiple Business Pages")
    print("="*70 + "\n")

    scraper = BusinessLLMScraper(output_dir="./scraped_data")

    # List of business page URLs to scrape
    business_urls = [
        "https://example.com/business/1",
        "https://example.com/business/2",
        "https://example.com/business/3",
    ]

    logger.info(f"Scraping {len(business_urls)} business pages...")

    try:
        # Scrape and save to file
        df, output_path = scraper.scrape_and_save(business_urls)

        if not df.empty:
            logger.info(f"Successfully scraped {len(df)} businesses")
            logger.info(f"Data saved to: {output_path}")
            logger.info(f"\nFirst few records:")
            print(df.head())
        else:
            logger.warning("No data extracted")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        scraper.close()


def example_3_discover_bulk_downloads():
    """Example 3: Discover bulk data download links"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Discover Bulk Download Links")
    print("="*70 + "\n")

    scraper = BusinessLLMScraper()

    # URLs to check for bulk data downloads
    check_urls = [
        "https://www.sos.ca.gov/business-programs/business-entities",
        "https://bizfileonline.sos.ca.gov/",
    ]

    for url in check_urls:
        logger.info(f"\nChecking {url} for download links...")

        try:
            downloads = scraper.discover_bulk_downloads(url)

            if downloads:
                logger.info(f"Found {len(downloads)} potential download links:")
                for i, dl in enumerate(downloads[:10], 1):  # Show first 10
                    logger.info(f"  {i}. {dl['text']}")
                    logger.info(f"     URL: {dl['url']}")
            else:
                logger.info("No download links found")

        except Exception as e:
            logger.error(f"Error checking {url}: {e}")

    scraper.close()


def example_4_custom_extraction():
    """Example 4: Custom data extraction with custom schema"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Data Extraction")
    print("="*70 + "\n")

    scraper = LLMScraper()

    # Define custom extraction schema
    custom_schema = {
        'page_title': {
            'type': 'string',
            'description': 'The main title of the page',
            'required': True
        },
        'contact_email': {
            'type': 'string',
            'description': 'Any contact email addresses found',
            'required': False
        },
        'contact_phone': {
            'type': 'string',
            'description': 'Any contact phone numbers found',
            'required': False
        },
        'description': {
            'type': 'string',
            'description': 'Brief description or summary of the page content',
            'required': False
        }
    }

    url = "https://example.com"

    logger.info(f"Extracting custom data from: {url}")

    try:
        data = scraper.scrape_page(
            url,
            custom_schema,
            additional_context="Extract contact and general information from this page"
        )

        if data:
            logger.info("Extracted data:")
            for key, value in data.items():
                if not key.startswith('_'):
                    logger.info(f"  {key}: {value}")
        else:
            logger.warning("No data extracted")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        scraper.close()


def example_5_extract_from_html_string():
    """Example 5: Extract data from HTML content directly"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Extract from HTML String")
    print("="*70 + "\n")

    scraper = LLMScraper()

    # Sample HTML content (in practice, this might come from a file or API)
    html_content = """
    <html>
        <body>
            <h1>Tech Solutions LLC</h1>
            <div class="info">
                <p>Entity Number: 123456789</p>
                <p>Type: Limited Liability Company</p>
                <p>Status: Active</p>
                <p>Registered: 2020-01-15</p>
                <p>Address: 123 Main St, San Francisco, CA 94102</p>
            </div>
        </body>
    </html>
    """

    schema = {
        'entity_name': 'The business name',
        'entity_number': 'The entity registration number',
        'entity_type': 'Type of business entity',
        'status': 'Current status',
        'registration_date': 'Registration date',
        'address': 'Business address'
    }

    logger.info("Converting HTML to markdown and extracting data...")

    try:
        # Convert HTML to markdown
        markdown = scraper.html_to_markdown(html_content)

        logger.info("Markdown content:")
        print(markdown)

        # Extract structured data
        data = scraper.extract_with_llm(markdown, schema)

        logger.info("\nExtracted structured data:")
        for key, value in data.items():
            logger.info(f"  {key}: {value}")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        scraper.close()


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("LLM SCRAPER EXAMPLES")
    print("="*70)

    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n⚠️  WARNING: ANTHROPIC_API_KEY environment variable not set!")
        print("\nTo run these examples, you need to set your Anthropic API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nYou can get an API key from: https://console.anthropic.com/")
        print("\nShowing example code structure only...\n")

    # Show what each example does
    print("\nAvailable Examples:")
    print("  1. Scrape single business page")
    print("  2. Scrape multiple business pages and save to CSV")
    print("  3. Discover bulk download links")
    print("  4. Custom data extraction with custom schema")
    print("  5. Extract data from HTML string")

    if api_key:
        print("\n✓ API key found - running examples...\n")

        # Uncomment examples you want to run
        # example_1_scrape_single_business()
        # example_2_scrape_multiple_businesses()
        example_3_discover_bulk_downloads()
        # example_4_custom_extraction()
        # example_5_extract_from_html_string()

    else:
        print("\nExample code templates shown above.")
        print("Set ANTHROPIC_API_KEY to run live examples.")

    print("\n" + "="*70)
    print("For more information, see:")
    print("  - README.md")
    print("  - test_llm_scraper.py")
    print("  - src/llm_scraper.py")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
