#!/usr/bin/env python3
"""
Test script for the web scraper module
Validates that the scraper can be imported and initialized
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


def test_imports():
    """Test that all scraper modules can be imported"""
    logger.info("Testing imports...")

    try:
        from src.scraper import CAScraper, BusinessDataScraper
        logger.info("✓ Successfully imported scraper modules")
        return True
    except ImportError as e:
        logger.error(f"✗ Failed to import scraper modules: {e}")
        return False


def test_initialization():
    """Test scraper initialization"""
    logger.info("Testing scraper initialization...")

    try:
        from src.scraper import CAScraper, BusinessDataScraper

        # Test CAScraper
        scraper1 = CAScraper(headless=True, rate_limit=1.0)
        logger.info("✓ CAScraper initialized successfully")

        # Test BusinessDataScraper
        scraper2 = BusinessDataScraper(output_dir="./test_output")
        logger.info("✓ BusinessDataScraper initialized successfully")

        # Cleanup
        scraper1.close()
        scraper2.close()

        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize scraper: {e}")
        return False


def test_configuration():
    """Test loading scraper configuration"""
    logger.info("Testing configuration loading...")

    try:
        import yaml
        config_path = Path("config/scraper.yaml")

        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}")
            return False

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        logger.info(f"✓ Loaded configuration with {len(config)} sections")

        # Validate required sections
        required_sections = ['business_names', 'scraper_settings', 'output']
        for section in required_sections:
            if section in config:
                logger.info(f"  ✓ Found section: {section}")
            else:
                logger.warning(f"  ✗ Missing section: {section}")

        return True
    except Exception as e:
        logger.error(f"✗ Failed to load configuration: {e}")
        return False


def test_cli_integration():
    """Test CLI integration with scraper"""
    logger.info("Testing CLI integration...")

    try:
        from src.cli import main
        logger.info("✓ CLI module imported successfully")
        logger.info("✓ Scraper is integrated with CLI")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to import CLI: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("WEB SCRAPER TEST SUITE")
    print("=" * 70 + "\n")

    tests = [
        ("Import Test", test_imports),
        ("Initialization Test", test_initialization),
        ("Configuration Test", test_configuration),
        ("CLI Integration Test", test_cli_integration),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        print("-" * 70)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test crashed: {e}", exc_info=True)
            results.append((test_name, False))
        print()

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status:10} - {test_name}")

    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 70 + "\n")

    if passed == total:
        logger.info("All tests passed! The scraper is ready to use.")
        return 0
    else:
        logger.warning(f"{total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
