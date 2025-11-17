# LLM-Based Web Scraper Guide

## Overview

The LLM-based scraper uses Claude AI to intelligently extract structured data from web pages, providing a robust alternative to traditional Selenium-based scraping.

### Why Use the LLM Scraper?

**Traditional Selenium Scraper Issues:**
- ❌ Brittle CSS selectors that break when websites change
- ❌ Requires ChromeDriver installation and maintenance
- ❌ Slow and resource-intensive
- ❌ Fails on dynamic JavaScript content
- ❌ Difficult to adapt to new website structures

**LLM Scraper Advantages:**
- ✅ No CSS selectors needed - understands content semantically
- ✅ Adapts automatically to website changes
- ✅ No browser or driver dependencies
- ✅ Handles any HTML structure
- ✅ Extracts data based on meaning, not structure
- ✅ Easy to customize extraction schema
- ✅ Works like Firecrawl but with full control

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This includes the new `anthropic` package for Claude API access.

### 2. Get Anthropic API Key

1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key

### 3. Set Environment Variable

```bash
# Linux/Mac
export ANTHROPIC_API_KEY='your-api-key-here'

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY='your-api-key-here'
```

Or add to your `.env` file:

```
ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

### Method 1: Command Line Interface

#### Scrape URLs with LLM Scraper

```bash
# Scrape specific URLs
python -m src.cli --llm-scrape --scrape-urls https://example.com/business1 https://example.com/business2 --output results

# Discover bulk download links using LLM scraper
python -m src.cli --discover-bulk --use-llm-scraper

# Download discovered bulk data files
python -m src.cli --discover-bulk --use-llm-scraper --download-bulk-data
```

#### Traditional Selenium Scraper (for comparison)

```bash
# Old Selenium-based scraping
python -m src.cli --scrape --business-names "Tech Corp" "Data LLC" --output results
```

### Method 2: Python API

#### Example 1: Basic Scraping

```python
from src.llm_scraper import BusinessLLMScraper

# Initialize scraper
scraper = BusinessLLMScraper()

# Scrape a single business page
business_data = scraper.scrape_business("https://example.com/business-page")

print(f"Business Name: {business_data.get('entity_name')}")
print(f"Status: {business_data.get('status')}")

scraper.close()
```

#### Example 2: Scrape Multiple Pages

```python
from src.llm_scraper import BusinessLLMScraper

scraper = BusinessLLMScraper(output_dir="./my_data")

# List of business page URLs
urls = [
    "https://example.com/business/1",
    "https://example.com/business/2",
    "https://example.com/business/3",
]

# Scrape and save to CSV
df, output_path = scraper.scrape_and_save(urls)

print(f"Scraped {len(df)} businesses")
print(f"Data saved to: {output_path}")

scraper.close()
```

#### Example 3: Custom Extraction Schema

```python
from src.llm_scraper import LLMScraper

scraper = LLMScraper()

# Define custom extraction schema
custom_schema = {
    'company_name': {
        'type': 'string',
        'description': 'The official company name',
        'required': True
    },
    'industry': {
        'type': 'string',
        'description': 'Primary industry or sector',
        'required': False
    },
    'employee_count': {
        'type': 'string',
        'description': 'Number of employees',
        'required': False
    },
    'revenue': {
        'type': 'string',
        'description': 'Annual revenue if available',
        'required': False
    }
}

# Scrape with custom schema
data = scraper.scrape_page(
    url="https://example.com/company-profile",
    extraction_schema=custom_schema,
    additional_context="Extract company financial and organizational information"
)

print(data)
scraper.close()
```

#### Example 4: Discover Download Links

```python
from src.llm_scraper import BusinessLLMScraper

scraper = BusinessLLMScraper()

# Find bulk data download links
downloads = scraper.discover_bulk_downloads(
    url="https://www.sos.ca.gov/business-programs/business-entities",
    download_patterns=[r'\.(zip|csv|xlsx)$']
)

for dl in downloads:
    print(f"{dl['text']}: {dl['url']}")

scraper.close()
```

#### Example 5: Extract from HTML String

```python
from src.llm_scraper import LLMScraper

scraper = LLMScraper()

html_content = """
<html>
    <body>
        <h1>Acme Corporation</h1>
        <p>Status: Active</p>
        <p>Founded: 2020-05-15</p>
        <p>Address: 123 Main St, Los Angeles, CA 90001</p>
    </body>
</html>
"""

schema = {
    'name': 'Company name',
    'status': 'Business status',
    'founded': 'Date founded',
    'address': 'Full address'
}

# Convert HTML to markdown
markdown = scraper.html_to_markdown(html_content)

# Extract structured data
data = scraper.extract_with_llm(markdown, schema)

print(data)
scraper.close()
```

## Features

### 1. Semantic Understanding

The LLM scraper understands content meaning, not just structure:

```python
# Works regardless of HTML structure
schema = {'company_name': 'The business name'}

# All of these will extract the company name correctly:
# <h1 class="title">Acme Corp</h1>
# <div class="business-name">Acme Corp</div>
# <span id="name">Acme Corp</span>
```

### 2. Flexible Schema Definition

Two ways to define extraction schemas:

**Simple Schema (string descriptions):**
```python
schema = {
    'name': 'The company name',
    'address': 'Business address',
    'phone': 'Contact phone number'
}
```

**Detailed Schema (with types and requirements):**
```python
schema = {
    'name': {
        'type': 'string',
        'description': 'Official company name',
        'required': True
    },
    'employees': {
        'type': 'array',
        'description': 'List of employee names',
        'required': False
    }
}
```

### 3. Automatic Pagination

Handle multi-page results:

```python
scraper = LLMScraper()

results = scraper.search_and_extract(
    search_url="https://example.com/search",
    search_params={'query': 'tech companies'},
    result_extraction_schema=schema,
    max_results=100,
    pagination_strategy="auto"
)
```

### 4. Rate Limiting

Built-in rate limiting to respect API limits:

```python
scraper = LLMScraper(
    rate_limit=2.0  # Minimum 2 seconds between requests
)
```

### 5. Retry Logic

Automatic retry with exponential backoff:

```python
scraper = LLMScraper(
    max_retries=3,  # Retry up to 3 times
    timeout=30       # 30 second timeout
)
```

## Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your-api-key

# Optional
DATA_INPUT_DIR=./input
DATA_OUTPUT_DIR=./output
```

### Model Selection

Choose different Claude models:

```python
# Use faster, cheaper model for simple tasks
scraper = LLMScraper(model="claude-3-haiku-20240307")

# Use most capable model for complex extraction
scraper = LLMScraper(model="claude-3-5-sonnet-20241022")  # Default

# Use Opus for highest quality (more expensive)
scraper = LLMScraper(model="claude-3-opus-20240229")
```

## Business Data Extraction

The `BusinessLLMScraper` class has a pre-configured schema for business entities:

```python
BUSINESS_SCHEMA = {
    'entity_number': 'Business entity number or ID',
    'entity_name': 'Official business name',
    'entity_type': 'Type of business entity (LLC, Corp, etc.)',
    'status': 'Current status (Active, Suspended, etc.)',
    'registration_date': 'Date registered',
    'jurisdiction': 'Jurisdiction of registration',
    'agent_name': 'Registered agent name',
    'principal_address': 'Principal business address',
    'mailing_address': 'Mailing address',
    'city': 'City',
    'state': 'State',
    'zip_code': 'ZIP code'
}
```

Use it directly:

```python
scraper = BusinessLLMScraper()
business = scraper.scrape_business("https://example.com/business/123")
```

## Testing

Run the test suite:

```bash
# Test LLM scraper installation and basic functionality
python test_llm_scraper.py

# Run example scripts
python example_llm_scraper.py
```

## Troubleshooting

### Error: "Anthropic library not available"

```bash
pip install anthropic
```

### Error: "ANTHROPIC_API_KEY not set"

```bash
export ANTHROPIC_API_KEY='your-key'
```

### Error: "Failed to parse JSON from LLM response"

The LLM might be returning unexpected format. Try:
1. Simplify your extraction schema
2. Add more specific descriptions
3. Use additional_context parameter to guide extraction

### Slow Performance

1. Use faster model: `model="claude-3-haiku-20240307"`
2. Reduce rate_limit: `rate_limit=0.5`
3. Limit content size (done automatically to first 15,000 chars)

## Best Practices

### 1. Schema Design

**Good Schema:**
```python
schema = {
    'company_name': 'The official registered business name',
    'status': 'Current business status (Active, Inactive, Suspended, etc.)'
}
```

**Bad Schema:**
```python
schema = {
    'name': 'name',  # Too vague
    'status': 'status'  # No context
}
```

### 2. Use Additional Context

```python
data = scraper.scrape_page(
    url,
    schema,
    additional_context="This is a business registration page from California SOS. Focus on extracting official entity information."
)
```

### 3. Handle Errors Gracefully

```python
try:
    data = scraper.scrape_business(url)
    if data and data.get('entity_name'):
        print(f"Success: {data['entity_name']}")
    else:
        print(f"No data extracted from {url}")
except Exception as e:
    print(f"Error scraping {url}: {e}")
```

### 4. Batch Processing

```python
results = []
for url in urls:
    try:
        data = scraper.scrape_business(url)
        if data:
            results.append(data)
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        continue

# Convert to DataFrame
df = pd.DataFrame(results)
```

## Cost Estimation

Claude API pricing (as of 2024):

- **Haiku**: $0.25 / million input tokens, $1.25 / million output tokens
- **Sonnet**: $3 / million input tokens, $15 / million output tokens
- **Opus**: $15 / million input tokens, $75 / million output tokens

Typical scraping costs:
- Simple page (~5,000 tokens): $0.015 - $0.09 with Sonnet
- Complex page (~15,000 tokens): $0.045 - $0.27 with Sonnet
- 100 pages with Sonnet: ~$4.50 - $27

Use Haiku for cost-effective scraping at scale.

## Comparison: Selenium vs LLM Scraper

| Feature | Selenium Scraper | LLM Scraper |
|---------|-----------------|-------------|
| **Setup** | Complex (ChromeDriver) | Simple (API key) |
| **Speed** | Slow (full browser) | Fast (HTTP only) |
| **Reliability** | Brittle (breaks on changes) | Robust (understands meaning) |
| **Maintenance** | High | Low |
| **Cost** | Free | ~$0.05-0.30 per page |
| **Dynamic JS** | Good | N/A (uses rendered HTML) |
| **Custom Schema** | Difficult | Easy |
| **Anti-bot Detection** | Detectable | Harder to detect |

## Examples

See complete working examples in:
- `example_llm_scraper.py` - Full usage examples
- `test_llm_scraper.py` - Test suite with examples
- `src/llm_scraper.py` - Source code with docstrings

## Support

For issues or questions:
1. Check this guide
2. Review example scripts
3. Check the source code documentation
4. Open an issue on GitHub

## License

Same as parent project.
