# Business Data Extraction Tool

A Python automation tool for extracting and filtering public business registration data from the California Secretary of State. This tool handles bulk data files (CSV/ZIP), applies customizable filters, validates data integrity, and exports results in multiple formats.

## Features

- **Web Scraping** 🆕
  - Scrape business data from CA SOS website
  - Search by business name or entity number
  - Automatic bulk data discovery
  - Rate limiting and retry logic
  - Selenium-based for JavaScript pages

- **Data Extraction**
  - Download bulk data from URLs
  - Process local CSV and ZIP files
  - Handle large files with chunked reading
  - Support for multiple file formats

- **Flexible Filtering**
  - Filter by entity type (LLC, Corporation, LP, etc.)
  - Filter by business status (Active, Suspended, etc.)
  - Location-based filtering (city, county, ZIP code)
  - Date range filtering
  - Business name pattern matching (regex support)
  - Custom field filters
  - Configurable via YAML

- **Data Validation**
  - Comprehensive data integrity checks
  - Null value detection
  - Duplicate detection
  - Data quality analysis
  - Detailed validation reports

- **Output Options**
  - Export to CSV, JSON, or Excel
  - Configurable output limits
  - Detailed extraction summaries

- **Web Interface** 🆕
  - Interactive web UI built with Streamlit
  - Drag-and-drop file upload
  - Visual data analytics with charts
  - Real-time filtering and preview
  - One-click downloads in multiple formats
  - No command line required!

## Quick Start - Web UI

The easiest way to use this tool is through the web interface:

```bash
# Install dependencies
pip install -r requirements.txt

# Launch web UI
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`

See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for complete web UI documentation.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Business-Data-Extraction-workflow
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Quick Start

### Web Interface (Recommended for Beginners)

**Launch the web UI:**
```bash
# Linux/macOS
./run_web_ui.sh

# Windows
run_web_ui.bat

# Or directly
streamlit run app.py
```

**Then:**
1. Upload your CSV or ZIP file
2. Configure filters in the sidebar
3. Preview and download results

See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for detailed instructions.

### Web Scraping (New!)

Scrape business data directly from the CA SOS website:

**Scrape by business name:**
```bash
python -m src.cli --scrape --business-names "Tech Solutions" "Consulting" --output scraped_data
```

**Discover bulk data downloads:**
```bash
python -m src.cli --discover-bulk --download-bulk-data
```

**Use configuration file:**
```bash
python -m src.cli --scrape --scrape-config config/scraper.yaml --output results
```

See [SCRAPER_GUIDE.md](SCRAPER_GUIDE.md) for complete scraping documentation.

### Command Line Usage (Advanced)

Extract data from a local CSV file:
```bash
python -m src.cli --input data/ca_businesses.csv --config config/filters.yaml --output results
```

Download and process bulk data:
```bash
python -m src.cli --download-url https://example.com/bulk-data.zip --config config/filters.yaml
```

Process all CSV files in a directory:
```bash
python -m src.cli --input-dir ./data --config config/filters.yaml --output filtered_results
```

### Programmatic Usage

```python
from src.extractor import DataExtractor
from src.filters import DataFilter
from src.validator import DataValidator

# Initialize extractor
extractor = DataExtractor(input_dir="./input", output_dir="./output")

# Read CSV data
df = extractor.read_csv("input/businesses.csv")

# Validate data
validator = DataValidator()
is_valid, report = validator.validate(df)

# Apply filters
filter_config = {
    'filters': {
        'entity_types': {
            'enabled': True,
            'values': ['DOMESTIC LIMITED LIABILITY COMPANY']
        },
        'status': {
            'enabled': True,
            'values': ['ACTIVE']
        }
    }
}

data_filter = DataFilter(filter_config)
filtered_df = data_filter.apply_filters(df)

# Export results
extractor.export_data(filtered_df, "output", format="csv")
```

## Configuration

### Filter Configuration (config/filters.yaml)

The tool uses a YAML configuration file to define filtering rules:

```yaml
filters:
  # Filter by entity type
  entity_types:
    enabled: true
    values:
      - "DOMESTIC LIMITED LIABILITY COMPANY"
      - "DOMESTIC STOCK"

  # Filter by status
  status:
    enabled: true
    values:
      - "ACTIVE"

  # Filter by registration date
  registration_date:
    enabled: true
    start_date: "2020-01-01"
    end_date: "2025-12-31"

  # Filter by location
  location:
    enabled: true
    cities:
      - "San Francisco"
      - "Los Angeles"

  # Filter by name patterns (regex)
  name_patterns:
    enabled: true
    patterns:
      - ".*Tech.*"
      - ".*Solutions.*"

output:
  format: "csv"
  max_records: 10000
```

### Environment Variables (.env)

```bash
# Data directories
DATA_INPUT_DIR=./input
DATA_OUTPUT_DIR=./output

# Bulk data source
BULK_DATA_URL=https://example.com/data.zip

# Filter configuration
FILTER_CONFIG_PATH=./config/filters.yaml

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/extraction.log
```

## CLI Options

### Input Options

- `--input FILE` - Process a single CSV or ZIP file
- `--input-dir DIR` - Process all CSV files in a directory
- `--download-url URL` - Download and process bulk data from URL

### Configuration

- `--config FILE` - Path to filter configuration YAML (default: config/filters.yaml)

### Output Options

- `--output FILE` - Output filename without extension (default: output/filtered_data)
- `--output-format {csv,json,excel}` - Output format (default: csv)
- `--output-dir DIR` - Output directory (default: output)

### Processing Options

- `--skip-validation` - Skip data validation step
- `--validation-report FILE` - Save validation report to file
- `--chunk-size N` - Chunk size for reading large files
- `--encoding ENC` - File encoding (default: utf-8)

### Logging Options

- `--log-level {DEBUG,INFO,WARNING,ERROR}` - Logging level (default: INFO)
- `--log-file FILE` - Save logs to file

## Data Sources

### California Secretary of State

The California SOS provides business entity data through their BizFile Online portal:

**Bulk Data Access (Updated 2024):**
1. Create an account at https://bizfileonline.sos.ca.gov/
2. Log in to your account
3. Navigate to "BE & UCC Bulk Orders" in the Information & Resources section
4. Order and download bulk data files (ZIP/CSV format)

**Important:** As of 2024, bulk data downloads require authentication and cannot be accessed publicly. The `--discover-bulk` feature will attempt to find any publicly available download links, but most bulk data now requires a registered account.

**Data Types Available:**
- Business Entities (Corporations, LLCs, LPs)
- Entity names and addresses
- Registration dates
- Entity status
- Agent information

**Alternative Options:**
- Use the web scraping feature to search and extract specific business records
- Contact bizfile@sos.ca.gov for questions about bulk data access
- Visit https://bizfileonline.sos.ca.gov/data-requests for data request information

**Note:** The California SOS does not provide a public API. This tool is designed to work with bulk data files downloaded from their portal or through web scraping individual records.

## Project Structure

```
Business-Data-Extraction-workflow/
├── src/
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # Command-line interface
│   ├── extractor.py        # Data extraction module
│   ├── filters.py          # Data filtering module
│   ├── validator.py        # Data validation module
│   └── scraper.py          # Web scraping module 🆕
├── config/
│   ├── filters.yaml        # Filter configuration
│   └── scraper.yaml        # Scraper configuration 🆕
├── input/                  # Input data directory
├── output/                 # Output data directory
├── scraped_data/           # Scraped data directory 🆕
├── logs/                   # Log files
├── app.py                  # Streamlit web UI
├── example.py              # Usage examples
├── requirements.txt        # Python dependencies
├── SCRAPER_GUIDE.md        # Scraper documentation 🆕
├── .env.example           # Environment template
└── README.md              # This file
```

## Examples

See `example.py` for detailed usage examples:

```bash
python example.py
```

Examples include:
1. Basic data extraction
2. Extraction with filters
3. Data validation
4. Download and process bulk data
5. Custom filtering logic

## Data Validation

The tool performs comprehensive data validation:

- **Row Count**: Ensures dataset is not empty
- **Column Presence**: Validates expected columns exist
- **Data Types**: Analyzes data types across columns
- **Null Values**: Reports missing data
- **Duplicates**: Detects duplicate records
- **Data Quality**: Identifies empty columns, single-value columns

Example validation report:
```
============================================================
DATA VALIDATION REPORT
============================================================
Overall Status: PASSED ✓
Checks Passed: 6/6

------------------------------------------------------------
VALIDATION DETAILS
------------------------------------------------------------
✓ Row Count: Dataset contains 45000 rows
✓ Column Presence: Dataset has 25 columns
✓ Data Types: Data types validated for 25 columns
✓ Null Values: 1250 null values found (1.11%)
✓ Duplicate Rows: 45 duplicate rows found (0.10%)
✓ Data Quality: No quality issues found
============================================================
```

## Filtering Capabilities

### Supported Filters

1. **Entity Type Filter**
   - Filter by business entity types
   - Examples: LLC, Corporation, Partnership

2. **Status Filter**
   - Filter by entity status
   - Examples: Active, Suspended, Dissolved

3. **Date Range Filter**
   - Filter by registration date ranges
   - Supports start and end dates

4. **Location Filter**
   - Filter by city, county, or ZIP code
   - Multiple locations supported

5. **Name Pattern Filter**
   - Filter by business name patterns
   - Full regex support
   - Case-insensitive matching

6. **Agent Filter**
   - Filter by registered agent names

7. **Custom Filters**
   - Define custom field:value filters
   - Flexible and extensible

## Troubleshooting

### Common Issues

**Issue: "File encoding error"**
- Solution: Try different encoding with `--encoding latin-1` or `--encoding cp1252`

**Issue: "Memory error with large files"**
- Solution: Use `--chunk-size 10000` to process files in chunks

**Issue: "Column not found" during filtering**
- Solution: Check your data file's column names and update filter config accordingly

**Issue: "No data after filtering"**
- Solution: Review filter criteria - they may be too restrictive

### Getting Help

For issues or questions:
1. Check the examples in `example.py`
2. Review the filter configuration in `config/filters.yaml`
3. Run with `--log-level DEBUG` for detailed logging

## Performance Tips

1. **Large Files**: Use `--chunk-size` for files > 1GB
2. **Multiple Files**: Process in batches if memory is limited
3. **Filters**: Apply most restrictive filters first for better performance
4. **Output Format**: CSV is fastest, Excel is slowest

## Development

### Running Tests

```bash
# Add tests in tests/ directory
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is provided as-is for business data extraction purposes.

## Support

For support with:
- **California SOS Data**: Visit https://www.sos.ca.gov/
- **Tool Issues**: Create an issue in the repository
- **Custom Features**: Contact the development team

## Acknowledgments

- California Secretary of State for providing public business data
- Python community for excellent data processing libraries

## Version History

### v1.0.0 (Initial Release)
- Data extraction from CSV/ZIP files
- Bulk data download support
- Flexible filtering system
- Data validation
- Multiple output formats
- Command-line interface
- Programmatic API
