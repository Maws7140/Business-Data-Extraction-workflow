# Web Scraper Guide

This guide explains how to use the web scraping functionality to gather business data from the California Secretary of State website.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Scraper Modes](#scraper-modes)
- [Configuration](#configuration)
- [CLI Usage](#cli-usage)
- [Programmatic Usage](#programmatic-usage)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The web scraper module allows you to:

- **Scrape individual business records** from the CA SOS business search
- **Discover bulk data download links** automatically
- **Download bulk data files** with one command
- **Extract business entity information** including names, addresses, status, and more
- **Handle rate limiting** and retries automatically

### Features

- Selenium-based scraping for JavaScript-heavy pages
- Automatic user agent rotation
- Rate limiting to be respectful to servers
- Retry logic with exponential backoff
- Progress tracking with progress bars
- Multiple output formats (CSV, JSON, Excel)

## Installation

### Prerequisites

The scraper requires additional dependencies:

```bash
pip install -r requirements.txt
```

This includes:
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parsing
- `selenium` - Browser automation
- `fake-useragent` - User agent rotation

### Chrome/Chromium WebDriver

For Selenium to work, you need Chrome/Chromium and ChromeDriver:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver
```

**macOS:**
```bash
brew install --cask google-chrome
brew install chromedriver
```

**Windows:**
Download ChromeDriver from https://chromedriver.chromium.org/

## Quick Start

### Scrape Business by Name

```bash
python -m src.cli --scrape --business-names "Tech Solutions" "Consulting Group" --output scraped_data
```

### Scrape by Entity Number

```bash
python -m src.cli --scrape --entity-numbers "202312345" "202356789" --output scraped_data
```

### Discover Bulk Data Downloads

```bash
python -m src.cli --discover-bulk
```

### Download Bulk Data Files

```bash
python -m src.cli --discover-bulk --download-bulk-data
```

## Scraper Modes

### 1. Business Search Mode (`--scrape`)

Scrapes individual business records from the CA SOS search.

**By Business Name:**
```bash
python -m src.cli --scrape \
  --business-names "Tech" "Consulting" \
  --max-scrape-results 50 \
  --output results/scraped
```

**By Entity Number:**
```bash
python -m src.cli --scrape \
  --entity-numbers "202312345" "202356789" \
  --output results/scraped
```

**Using Configuration File:**
```bash
python -m src.cli --scrape \
  --scrape-config config/scraper.yaml \
  --output results/scraped
```

### 2. Bulk Discovery Mode (`--discover-bulk`)

Finds and lists available bulk data downloads from CA SOS.

**List Available Downloads:**
```bash
python -m src.cli --discover-bulk
```

**Download All Bulk Files:**
```bash
python -m src.cli --discover-bulk --download-bulk-data
```

## Configuration

### Scraper Configuration File

Create `config/scraper.yaml` (see example in config directory):

```yaml
# Business names to search for
business_names:
  - "Tech Solutions"
  - "Consulting Group"

# Entity numbers to scrape
entity_numbers: []

# Maximum results per search
max_results: 100

# Scraper behavior
scraper_settings:
  headless: true        # Run browser without GUI
  rate_limit: 2.0       # Seconds between requests
  timeout: 30           # Request timeout
  max_retries: 3        # Retry attempts

# Output settings
output:
  output_dir: "./scraped_data"
  format: "csv"
  include_timestamp: true
```

## CLI Usage

### Complete CLI Options

**Scraping Options:**
- `--scrape` - Enable scraping mode
- `--business-names NAME [NAME ...]` - Business names to search
- `--entity-numbers NUM [NUM ...]` - Entity numbers to search
- `--scrape-config FILE` - Path to scraper config YAML
- `--max-scrape-results N` - Max results per search (default: 100)

**Bulk Data Options:**
- `--discover-bulk` - Find bulk data download links
- `--download-bulk-data` - Download discovered bulk files

**Standard Options:**
- `--output FILE` - Output filename
- `--output-format {csv,json,excel}` - Output format
- `--output-dir DIR` - Output directory
- `--config FILE` - Filter configuration (applied after scraping)
- `--log-level {DEBUG,INFO,WARNING,ERROR}` - Logging level

### Examples

**1. Scrape and Filter:**

```bash
# Scrape businesses, then apply filters
python -m src.cli --scrape \
  --business-names "Technology" \
  --config config/filters.yaml \
  --output filtered_scraped
```

**2. Scrape Multiple Entities:**

```bash
python -m src.cli --scrape \
  --entity-numbers "C1234567" "C2345678" "C3456789" \
  --output-format json \
  --output entities
```

**3. Discover and Download Bulk Data:**

```bash
# First discover available files
python -m src.cli --discover-bulk

# Then download them
python -m src.cli --discover-bulk --download-bulk-data
```

**4. Complete Workflow:**

```bash
# 1. Scrape data
python -m src.cli --scrape \
  --scrape-config config/scraper.yaml \
  --output scraped/raw_data

# 2. Process with filters
python -m src.cli --input scraped/raw_data.csv \
  --config config/filters.yaml \
  --output results/filtered
```

## Programmatic Usage

### Basic Scraping

```python
from src.scraper import BusinessDataScraper

# Initialize scraper
scraper = BusinessDataScraper(output_dir="./scraped")

# Configure search
search_config = {
    'business_names': ['Tech Solutions', 'Consulting'],
    'entity_numbers': [],
    'max_results': 50
}

# Scrape and save
df, output_path = scraper.scrape_and_save(search_config)
print(f"Scraped {len(df)} records to {output_path}")

# Cleanup
scraper.close()
```

### Advanced Scraping

```python
from src.scraper import CAScraper
import pandas as pd

# Initialize with custom settings
scraper = CAScraper(
    headless=True,
    rate_limit=2.0,
    timeout=30,
    max_retries=3
)

# Search businesses
results = scraper.search_business(
    business_name="Technology",
    max_results=100
)

# Convert to DataFrame
df = pd.DataFrame(results)

# Cleanup
scraper.close()
```

### Discover Bulk Data

```python
from src.scraper import BusinessDataScraper

scraper = BusinessDataScraper()

# Discover downloads
downloads = scraper.discover_bulk_downloads(
    download_all=True,
    output_dir=Path("./bulk_data")
)

for download in downloads:
    print(f"Downloaded: {download['filename']}")
    print(f"Location: {download['local_path']}")

scraper.close()
```

## Best Practices

### 1. Rate Limiting

Always use appropriate rate limiting to avoid overwhelming servers:

```yaml
scraper_settings:
  rate_limit: 2.0  # Minimum 2 seconds between requests
```

For large-scale scraping, increase this to 3-5 seconds.

### 2. Error Handling

Enable retry logic for reliability:

```yaml
scraper_settings:
  max_retries: 3
  ignore_errors: true
```

### 3. Respectful Scraping

- **Scrape during off-peak hours** (late night/early morning)
- **Use reasonable page limits** - don't scrape entire database
- **Cache results** - don't re-scrape the same data
- **Monitor for rate limiting** - back off if you get blocked

### 4. Data Validation

Always validate scraped data:

```bash
python -m src.cli --scrape \
  --business-names "Tech" \
  --output scraped \
  --validation-report validation.txt
```

### 5. Incremental Scraping

For large datasets, scrape in batches:

```python
# Batch 1
scraper.scrape_and_save({
    'business_names': ['Tech'],
    'max_results': 100
}, 'batch1.csv')

# Wait between batches
time.sleep(60)

# Batch 2
scraper.scrape_and_save({
    'business_names': ['Consulting'],
    'max_results': 100
}, 'batch2.csv')
```

## Troubleshooting

### Common Issues

**Issue: "ChromeDriver not found"**

Solution:
```bash
# Install ChromeDriver
sudo apt-get install chromium-chromedriver  # Linux
brew install chromedriver                    # macOS
```

**Issue: "Element not found" errors**

Cause: Website structure changed or page didn't load

Solution:
- Update CSS selectors in `scraper.py`
- Increase timeout value
- Enable debug logging

```bash
python -m src.cli --scrape --business-names "Tech" --log-level DEBUG
```

**Issue: Getting blocked or rate limited**

Solution:
- Increase `rate_limit` in config
- Use headless mode
- Reduce `max_results`
- Add random delays

**Issue: Incomplete data scraped**

Solution:
- Check if JavaScript is required (use Selenium)
- Increase page load wait time
- Verify CSS selectors match website structure

**Issue: Memory errors with large scrapes**

Solution:
- Reduce `max_results`
- Scrape in batches
- Use CSV output instead of loading all in memory

### Debug Mode

Run with debug logging to troubleshoot:

```bash
python -m src.cli --scrape \
  --business-names "Test" \
  --log-level DEBUG \
  --log-file logs/scraper_debug.log
```

### Viewing Raw HTML

Enable HTML saving for debugging:

```yaml
advanced:
  save_html: true
```

This saves page HTML to `scraped_data/html/` for inspection.

## Legal and Ethical Considerations

### Public Data

The CA SOS website provides public business registration data. However:

- **Read and comply** with the website's Terms of Service
- **Respect robots.txt** directives
- **Don't overwhelm** the server with requests
- **Use bulk downloads** when available instead of scraping individual pages

### Appropriate Use

This scraper should be used for:
- Research and analysis
- Business intelligence
- Academic purposes
- Compliance and verification

Do NOT use for:
- Spamming or unsolicited marketing
- Harassment
- Violation of privacy laws
- Any illegal purposes

## Performance Tips

1. **Use bulk downloads when possible** - Much faster than scraping
2. **Scrape during off-peak hours** - Better performance
3. **Enable headless mode** - Faster than GUI browser
4. **Optimize selectors** - Use efficient CSS selectors
5. **Cache results** - Store and reuse scraped data
6. **Use filters** - Apply filters to reduce data volume

## Support

For issues with the scraper:

1. Check logs in `logs/scraper.log`
2. Run with `--log-level DEBUG`
3. Verify ChromeDriver installation
4. Check CA SOS website for changes
5. Review CSS selectors in `scraper.py`

## Updates

The CA SOS website may change over time. If the scraper stops working:

1. Inspect the website structure with browser dev tools
2. Update CSS selectors in `src/scraper.py`
3. Adjust wait times and timeouts
4. Update the configuration as needed

For assistance, check the project repository for updates and fixes.
