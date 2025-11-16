# Usage Examples

Comprehensive examples for using the Business Data Extraction Tool.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Advanced Filtering](#advanced-filtering)
3. [Working with Large Files](#working-with-large-files)
4. [Batch Processing](#batch-processing)
5. [Custom Workflows](#custom-workflows)
6. [Troubleshooting](#troubleshooting)

## Basic Usage

### Example 1: Extract All Active LLCs

```bash
python -m src.cli \
  --input input/sample_data.csv \
  --config config/filters.yaml \
  --output output/active_llcs
```

**Filter Configuration (config/filters.yaml):**
```yaml
filters:
  entity_types:
    enabled: true
    values:
      - "DOMESTIC LIMITED LIABILITY COMPANY"

  status:
    enabled: true
    values:
      - "ACTIVE"
```

### Example 2: Extract by Location

Extract all businesses in San Francisco:

```yaml
filters:
  location:
    enabled: true
    cities:
      - "San Francisco"
```

```bash
python -m src.cli \
  --input input/california_businesses.csv \
  --config config/sf_filter.yaml \
  --output output/sf_businesses \
  --output-format excel
```

### Example 3: Recent Registrations

Extract businesses registered in 2024:

```yaml
filters:
  registration_date:
    enabled: true
    start_date: "2024-01-01"
    end_date: "2024-12-31"
```

```bash
python -m src.cli \
  --input input/data.csv \
  --config config/recent_filter.yaml \
  --output output/2024_registrations
```

## Advanced Filtering

### Example 4: Multiple Criteria

Extract tech companies in major cities:

```yaml
filters:
  entity_types:
    enabled: true
    values:
      - "DOMESTIC LIMITED LIABILITY COMPANY"
      - "DOMESTIC STOCK"

  status:
    enabled: true
    values:
      - "ACTIVE"

  location:
    enabled: true
    cities:
      - "San Francisco"
      - "San Jose"
      - "Palo Alto"
      - "Mountain View"

  name_patterns:
    enabled: true
    patterns:
      - ".*Tech.*"
      - ".*Software.*"
      - ".*Digital.*"
      - ".*AI.*"
```

### Example 5: Name Pattern Matching

Extract companies with specific keywords:

```yaml
filters:
  name_patterns:
    enabled: true
    patterns:
      - ".*Solutions.*"
      - ".*Services.*"
      - ".*Consulting.*"
```

### Example 6: Agent-Based Filtering

Extract all businesses using specific registered agents:

```yaml
filters:
  agent:
    enabled: true
    agent_names:
      - "ABC Legal Services"
      - "XYZ Registered Agents"
```

## Working with Large Files

### Example 7: Process Large CSV with Chunking

For files > 1GB:

```bash
python -m src.cli \
  --input input/large_dataset.csv \
  --config config/filters.yaml \
  --chunk-size 50000 \
  --output output/filtered_large \
  --log-level INFO
```

### Example 8: Download and Process Bulk Data

```bash
python -m src.cli \
  --download-url https://example.com/ca-sos-bulk-data.zip \
  --config config/filters.yaml \
  --output output/bulk_results \
  --validation-report output/validation.txt
```

### Example 9: Limit Output Size

Process large file but limit output:

```yaml
output:
  format: "csv"
  max_records: 10000
```

```bash
python -m src.cli \
  --input input/huge_file.csv \
  --config config/limited_output.yaml \
  --output output/top_10k
```

## Batch Processing

### Example 10: Process Multiple Files

```bash
python -m src.cli \
  --input-dir ./input/batch_files \
  --config config/filters.yaml \
  --output output/combined_results
```

### Example 11: Process with Validation Reports

```bash
for file in input/*.csv; do
  filename=$(basename "$file" .csv)
  python -m src.cli \
    --input "$file" \
    --config config/filters.yaml \
    --output "output/${filename}_filtered" \
    --validation-report "output/${filename}_validation.txt"
done
```

### Example 12: Export to Multiple Formats

```bash
# Export as CSV
python -m src.cli --input input/data.csv --config config/filters.yaml \
  --output output/results --output-format csv

# Export as JSON
python -m src.cli --input input/data.csv --config config/filters.yaml \
  --output output/results --output-format json

# Export as Excel
python -m src.cli --input input/data.csv --config config/filters.yaml \
  --output output/results --output-format excel
```

## Custom Workflows

### Example 13: Programmatic Usage

```python
from pathlib import Path
from src.extractor import DataExtractor
from src.filters import DataFilter
from src.validator import DataValidator
import yaml

# Load configuration
with open('config/filters.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize components
extractor = DataExtractor(input_dir="./input", output_dir="./output")
validator = DataValidator()
data_filter = DataFilter(config)

# Process data
df = extractor.read_csv(Path("input/businesses.csv"))

# Validate
is_valid, report = validator.validate(df)
print(validator.get_validation_report())

# Filter
filtered_df = data_filter.apply_filters(df)
filtered_df = data_filter.apply_output_limits(filtered_df)

# Export
extractor.export_data(filtered_df, "custom_output", format="csv")

print(f"Processed {len(df)} -> {len(filtered_df)} records")
```

### Example 14: Custom Filtering Logic

```python
import pandas as pd
from src.extractor import DataExtractor

extractor = DataExtractor()
df = extractor.read_csv("input/data.csv")

# Custom pandas filtering
filtered = df[
    (df['ENTITY_TYPE'] == 'DOMESTIC LIMITED LIABILITY COMPANY') &
    (df['STATUS'] == 'ACTIVE') &
    (df['REGISTRATION_DATE'] >= '2024-01-01') &
    (df['CITY'].isin(['San Francisco', 'Los Angeles'])) &
    (df['ENTITY_NAME'].str.contains('Tech|Software', case=False, regex=True))
]

# Export
extractor.export_data(filtered, "custom_filtered", format="excel")
```

### Example 15: Pipeline Processing

```python
from pathlib import Path
from src.extractor import DataExtractor
from src.filters import DataFilter
from src.validator import DataValidator

def process_pipeline(input_file, output_file):
    """Complete processing pipeline"""

    # Initialize
    extractor = DataExtractor()
    validator = DataValidator()

    # Load
    print(f"Loading {input_file}...")
    df = extractor.read_csv(Path(input_file))

    # Validate
    print("Validating...")
    is_valid, _ = validator.validate(df)

    if not is_valid:
        print("Warning: Validation issues detected")

    # Filter
    print("Filtering...")
    config = {
        'filters': {
            'status': {'enabled': True, 'values': ['ACTIVE']},
        },
        'output': {'max_records': None}
    }

    data_filter = DataFilter(config)
    filtered = data_filter.apply_filters(df)

    # Export
    print(f"Exporting to {output_file}...")
    extractor.export_data(filtered, output_file, format="csv")

    print(f"Done! {len(df)} -> {len(filtered)} records")

# Run pipeline
process_pipeline("input/data.csv", "output/processed")
```

## Real-World Scenarios

### Example 16: Find All Tech Startups in Bay Area

```yaml
filters:
  entity_types:
    enabled: true
    values:
      - "DOMESTIC LIMITED LIABILITY COMPANY"

  status:
    enabled: true
    values:
      - "ACTIVE"

  registration_date:
    enabled: true
    start_date: "2023-01-01"
    end_date: "2025-12-31"

  location:
    enabled: true
    cities:
      - "San Francisco"
      - "Oakland"
      - "Berkeley"
      - "San Jose"
      - "Palo Alto"
      - "Mountain View"
      - "Sunnyvale"

  name_patterns:
    enabled: true
    patterns:
      - ".*Tech.*"
      - ".*AI.*"
      - ".*Software.*"
      - ".*Digital.*"
      - ".*Data.*"
```

### Example 17: Market Research - Restaurant Industry

```yaml
filters:
  status:
    enabled: true
    values:
      - "ACTIVE"

  name_patterns:
    enabled: true
    patterns:
      - ".*Restaurant.*"
      - ".*Cafe.*"
      - ".*Coffee.*"
      - ".*Bistro.*"
      - ".*Diner.*"
      - ".*Eatery.*"

  location:
    enabled: true
    cities:
      - "Los Angeles"
      - "San Diego"
```

### Example 18: Competitor Analysis

```yaml
filters:
  entity_types:
    enabled: true
    values:
      - "DOMESTIC STOCK"
      - "FOREIGN STOCK"

  status:
    enabled: true
    values:
      - "ACTIVE"

  name_patterns:
    enabled: true
    patterns:
      - ".*Consulting.*"

  registration_date:
    enabled: true
    start_date: "2022-01-01"
```

## Troubleshooting

### Example 19: Debug Mode

Run with detailed logging:

```bash
python -m src.cli \
  --input input/data.csv \
  --config config/filters.yaml \
  --output output/results \
  --log-level DEBUG \
  --log-file logs/debug.log
```

### Example 20: Handle Encoding Issues

If you encounter encoding errors:

```bash
# Try Latin-1 encoding
python -m src.cli \
  --input input/data.csv \
  --encoding latin-1 \
  --config config/filters.yaml \
  --output output/results

# Or Windows encoding
python -m src.cli \
  --input input/data.csv \
  --encoding cp1252 \
  --config config/filters.yaml \
  --output output/results
```

### Example 21: Skip Validation for Speed

```bash
python -m src.cli \
  --input input/trusted_data.csv \
  --config config/filters.yaml \
  --skip-validation \
  --output output/fast_results
```

## Performance Tips

### Example 22: Optimize for Large Datasets

```bash
# Use chunking for files > 1GB
# Skip validation if data is trusted
# Output to CSV (fastest format)

python -m src.cli \
  --input input/huge_file.csv \
  --chunk-size 100000 \
  --skip-validation \
  --config config/filters.yaml \
  --output output/optimized \
  --output-format csv
```

### Example 23: Incremental Processing

```python
# Process large dataset in chunks and combine
from src.extractor import DataExtractor
from src.filters import DataFilter
import pandas as pd

extractor = DataExtractor()
data_filter = DataFilter(config)

# Read in chunks
chunks = pd.read_csv('input/large_file.csv', chunksize=50000)

results = []
for chunk in chunks:
    filtered = data_filter.apply_filters(chunk)
    results.append(filtered)

# Combine
final = pd.concat(results, ignore_index=True)
extractor.export_data(final, "incremental_results")
```

## Summary

These examples demonstrate:
- Basic extraction and filtering
- Advanced multi-criteria filtering
- Large file handling
- Batch processing
- Custom programmatic workflows
- Real-world use cases
- Performance optimization
- Troubleshooting techniques

For more information, see:
- `README.md` - Full documentation
- `SETUP.md` - Installation guide
- `example.py` - Code examples
- `config/filters.yaml` - Filter configuration reference
