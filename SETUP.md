# Setup Guide

Complete setup instructions for the Business Data Extraction Tool.

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB+ recommended for large datasets)
- **Disk Space**: 10GB+ (depending on data size)

## Installation Steps

### 1. Install Python

If you don't have Python installed:

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run installer and check "Add Python to PATH"
3. Verify: `python --version`

**macOS:**
```bash
# Using Homebrew
brew install python3

# Verify
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip

# Verify
python3 --version
```

### 2. Clone or Download the Project

```bash
# Using Git
git clone <repository-url>
cd Business-Data-Extraction-workflow

# Or download ZIP and extract
```

### 3. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `pandas` - Data manipulation
- `requests` - HTTP downloads
- `python-dotenv` - Environment variables
- `pyyaml` - YAML configuration
- `tqdm` - Progress bars
- `openpyxl` - Excel support

### 5. Create Directory Structure

The tool will create directories automatically, but you can set them up manually:

```bash
mkdir -p input output logs config
```

### 6. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (optional)
nano .env  # or use your preferred editor
```

### 7. Configure Filters

Review and customize the filter configuration:

```bash
# Edit filter configuration
nano config/filters.yaml
```

Customize based on your needs:
- Entity types you want to extract
- Status filters (Active, Suspended, etc.)
- Date ranges
- Location filters
- Name patterns

### 8. Verify Installation

```bash
# Run the CLI with help flag
python -m src.cli --help

# Should display help information
```

## Getting Sample Data

### California Secretary of State Data

1. Visit: https://www.sos.ca.gov/business-programs/bizfile
2. Click "Business Entity Records"
3. Navigate to "Bulk Data Orders"
4. Order and download bulk data file
5. Save to `input/` directory

**Note:** Bulk data files may require registration and/or payment.

### Testing with Sample Data

For testing purposes, create a sample CSV file:

```bash
# Create sample data file
cat > input/sample_data.csv << 'EOF'
ENTITY_NAME,ENTITY_TYPE,STATUS,CITY,REGISTRATION_DATE
Tech Solutions LLC,DOMESTIC LIMITED LIABILITY COMPANY,ACTIVE,San Francisco,2024-01-15
ABC Corporation,DOMESTIC STOCK,ACTIVE,Los Angeles,2023-06-20
XYZ Partners,DOMESTIC LIMITED PARTNERSHIP,SUSPENDED,San Diego,2022-03-10
EOF
```

## First Run

### Test the Installation

```bash
# Run with sample data
python -m src.cli \
  --input input/sample_data.csv \
  --config config/filters.yaml \
  --output test_output

# Check the output
ls -lh output/
cat output/test_output.csv
```

### Expected Output

You should see:
1. Console output showing extraction progress
2. Validation report (if not skipped)
3. Filtering progress
4. Extraction summary
5. Output file in `output/` directory

## Configuration Details

### Environment Variables (.env)

```bash
# Input/Output directories
DATA_INPUT_DIR=./input
DATA_OUTPUT_DIR=./output

# Bulk data URL (if applicable)
BULK_DATA_URL=https://example.com/ca-sos-data.zip

# Filter configuration
FILTER_CONFIG_PATH=./config/filters.yaml

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/extraction.log
```

### Filter Configuration (config/filters.yaml)

Key sections to customize:

1. **Entity Types**
   ```yaml
   entity_types:
     enabled: true
     values:
       - "DOMESTIC LIMITED LIABILITY COMPANY"
       - "DOMESTIC STOCK"
   ```

2. **Status Filter**
   ```yaml
   status:
     enabled: true
     values:
       - "ACTIVE"
   ```

3. **Date Range**
   ```yaml
   registration_date:
     enabled: true
     start_date: "2020-01-01"
     end_date: "2025-12-31"
   ```

4. **Location**
   ```yaml
   location:
     enabled: true
     cities:
       - "San Francisco"
       - "Los Angeles"
   ```

5. **Output Settings**
   ```yaml
   output:
     format: "csv"
     max_records: 10000
   ```

## Troubleshooting Setup

### Python Not Found

**Error:** `python: command not found`

**Solution:**
- On some systems, use `python3` instead of `python`
- Verify Python is installed: `which python` or `which python3`
- Check PATH includes Python directory

### Permission Denied

**Error:** `Permission denied` when running commands

**Solution:**
```bash
# On Linux/macOS, make script executable
chmod +x example.py

# Run with python explicitly
python example.py
```

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'pandas'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

### pip Install Fails

**Error:** Various errors during `pip install`

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install with --user flag
pip install --user -r requirements.txt

# Or use pip3
pip3 install -r requirements.txt
```

### Encoding Issues

**Error:** `UnicodeDecodeError` when reading files

**Solution:**
```bash
# Try different encoding
python -m src.cli --input data.csv --encoding latin-1

# Or
python -m src.cli --input data.csv --encoding cp1252
```

## Next Steps

After successful setup:

1. **Review Documentation**
   - Read `README.md` for detailed usage
   - Check `example.py` for code examples

2. **Obtain Real Data**
   - Download CA SOS bulk data
   - Place in `input/` directory

3. **Customize Filters**
   - Edit `config/filters.yaml`
   - Match your specific requirements

4. **Run Extraction**
   ```bash
   python -m src.cli \
     --input input/your_data.csv \
     --config config/filters.yaml \
     --output results
   ```

5. **Review Results**
   - Check `output/` directory
   - Review validation reports
   - Verify filtered data

## Advanced Setup

### Running as a Service

For automated/scheduled extraction:

**Linux (systemd):**
Create `/etc/systemd/system/data-extraction.service`:
```ini
[Unit]
Description=Business Data Extraction
After=network.target

[Service]
Type=oneshot
User=yourusername
WorkingDirectory=/path/to/Business-Data-Extraction-workflow
ExecStart=/path/to/venv/bin/python -m src.cli --input input/data.csv --config config/filters.yaml

[Install]
WantedBy=multi-user.target
```

**Scheduled with Cron:**
```bash
# Edit crontab
crontab -e

# Add daily extraction at 2 AM
0 2 * * * cd /path/to/Business-Data-Extraction-workflow && /path/to/venv/bin/python -m src.cli --input input/data.csv --config config/filters.yaml
```

### Docker Setup (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "src.cli", "--help"]
```

Build and run:
```bash
docker build -t data-extraction .
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output data-extraction
```

## Getting Help

If you encounter issues:

1. Check logs: `cat logs/extraction.log`
2. Run with debug mode: `--log-level DEBUG`
3. Review error messages carefully
4. Check file permissions
5. Verify data format matches expectations

## Support Resources

- **Documentation**: README.md
- **Examples**: example.py
- **Configuration**: config/filters.yaml
- **California SOS**: https://www.sos.ca.gov/

## Updating

To update the tool:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt
```

---

**Setup Complete!** You're ready to start extracting business data.
