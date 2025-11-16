# Quick Start Guide

Get started with the Business Data Extraction Tool in 5 minutes!

## Installation (One-Time Setup)

### 1. Install Python

Make sure you have Python 3.8 or higher:
```bash
python --version
# or
python3 --version
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

That's it! Installation complete.

## Using the Web UI (Easiest)

### Launch the Application

**Linux/macOS:**
```bash
./run_web_ui.sh
```

**Windows:**
```cmd
run_web_ui.bat
```

**Or directly:**
```bash
streamlit run app.py
```

### Using the Interface

1. **Browser opens automatically** at http://localhost:8501

2. **Load data:**
   - Click "Browse files" in sidebar
   - Select your CSV or ZIP file
   - Click "📥 Load Data"
   - Or use "Sample Data" to try it out

3. **Review your data:**
   - See overview metrics
   - Preview data table
   - Check validation results

4. **Apply filters** (in sidebar):
   - ☑️ Enable desired filters
   - Select filter values
   - Click "▶ Apply Filters"

5. **Download results:**
   - Click "📥 Download CSV" (or JSON/Excel)
   - File saves to your Downloads folder

**Done!** You've filtered and extracted your data.

## Using the Command Line (Advanced)

### Basic Usage

```bash
python -m src.cli \
  --input your_data.csv \
  --config config/filters.yaml \
  --output results
```

### With Sample Data

```bash
python -m src.cli \
  --input input/sample_data.csv \
  --config config/filters.yaml \
  --output sample_results
```

Results saved to: `output/sample_results.csv`

## Example: Filter Active LLCs in San Francisco

### 1. Edit Filter Config

Edit `config/filters.yaml`:

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

  location:
    enabled: true
    cities:
      - "San Francisco"
```

### 2. Run Extraction

**Web UI:**
1. Load your data
2. In sidebar:
   - ☑️ Enable Entity Type Filter → Select "DOMESTIC LIMITED LIABILITY COMPANY"
   - ☑️ Enable Status Filter → Select "ACTIVE"
   - ☑️ Enable Location Filter → Select "San Francisco"
3. Click "▶ Apply Filters"
4. Download results

**CLI:**
```bash
python -m src.cli \
  --input input/sample_data.csv \
  --config config/filters.yaml \
  --output sf_active_llcs
```

## Common Tasks

### Task 1: Process Downloaded CA SOS Data

1. Download bulk data from https://www.sos.ca.gov/business-programs/bizfile
2. Save to `input/` folder
3. Web UI:
   - Upload the file
   - Configure filters
   - Download results
4. CLI:
   ```bash
   python -m src.cli --input input/ca_sos_data.zip --config config/filters.yaml
   ```

### Task 2: Find Tech Companies

**Filter Config:**
```yaml
filters:
  name_patterns:
    enabled: true
    patterns:
      - ".*Tech.*"
      - ".*Software.*"
      - ".*AI.*"
```

**Web UI:**
- ☑️ Enable Name Pattern Filter
- Enter: `.*Tech.*|.*Software.*|.*AI.*`

### Task 3: Recent Registrations (2024)

**Filter Config:**
```yaml
filters:
  registration_date:
    enabled: true
    start_date: "2024-01-01"
    end_date: "2024-12-31"
```

**Web UI:**
- ☑️ Enable Date Range Filter
- Start: 2024-01-01
- End: 2024-12-31

## Tips

### Start Small
- Use sample data first
- Test your filters
- Then process real data

### Web UI vs CLI

**Use Web UI when:**
- Learning the tool
- Exploring data
- One-time extraction
- Need visualizations

**Use CLI when:**
- Processing large files (> 1GB)
- Automating tasks
- Batch processing
- Integration with other tools

### Performance

**Large files:**
```bash
# Use chunking for files > 1GB
python -m src.cli \
  --input large_file.csv \
  --chunk-size 50000 \
  --config config/filters.yaml
```

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Web UI won't start
```bash
# Install Streamlit
pip install streamlit plotly

# Try again
streamlit run app.py
```

### File encoding issues
```bash
# Try different encoding
python -m src.cli --input data.csv --encoding latin-1
```

## Next Steps

### Learn More

- **Full Documentation**: [README.md](README.md)
- **Web UI Guide**: [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md)
- **Setup Guide**: [SETUP.md](SETUP.md)
- **Code Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)

### Customize

1. **Edit filters**: `config/filters.yaml`
2. **Set environment**: `.env` file
3. **Try examples**: `python example.py`

### Automate

Create a script for repeated tasks:

```bash
#!/bin/bash
# my_extraction.sh

python -m src.cli \
  --input /path/to/data.csv \
  --config my_custom_filters.yaml \
  --output results_$(date +%Y%m%d) \
  --validation-report validation_$(date +%Y%m%d).txt
```

## Support

- Check documentation in this repository
- Review error messages carefully
- Try with sample data first
- Use `--log-level DEBUG` for detailed logs

## Summary

**Fastest way to get started:**
```bash
pip install -r requirements.txt
streamlit run app.py
# Load sample data and explore!
```

That's it! You're ready to extract business data.

---

**Need help?** See [README.md](README.md) for comprehensive documentation.
