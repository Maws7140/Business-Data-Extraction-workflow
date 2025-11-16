# Web UI Guide

Complete guide for using the Business Data Extraction Tool Web Interface.

## Overview

The web UI provides an intuitive, interactive interface for extracting and filtering business data without using the command line. Built with Streamlit, it offers:

- **Drag-and-drop file upload**
- **Interactive filter configuration**
- **Real-time data preview**
- **Visual analytics with charts**
- **One-click downloads** in multiple formats

## Installation

### Prerequisites

Ensure you have Python 3.8+ and all dependencies installed:

```bash
pip install -r requirements.txt
```

This will install:
- Streamlit (web framework)
- Plotly (interactive charts)
- All other required packages

## Starting the Web UI

### Option 1: Using Launch Scripts

**Linux/macOS:**
```bash
chmod +x run_web_ui.sh
./run_web_ui.sh
```

**Windows:**
```cmd
run_web_ui.bat
```

### Option 2: Direct Command

```bash
streamlit run app.py
```

### What Happens Next

1. The web server starts on `http://localhost:8501`
2. Your default browser opens automatically
3. The application loads and is ready to use

## Using the Web UI

### Step 1: Load Data

#### Upload File

1. In the sidebar, ensure "Upload File" is selected
2. Click "Browse files"
3. Select a CSV or ZIP file
4. Click "📥 Load Data"
5. Wait for processing (progress indicator shows status)

#### Use Sample Data

1. In the sidebar, select "Use Sample Data"
2. Click "Load Sample Data"
3. Sample data loads instantly for testing

### Step 2: Explore Data (Overview Tab)

The **Overview** tab shows:

#### Metrics Dashboard
- **Total Records**: Number of rows in dataset
- **Columns**: Number of fields
- **Null Values**: Percentage of missing data
- **Memory Usage**: Dataset size in MB

#### Data Preview
- First 100 rows displayed in interactive table
- Sortable columns
- Searchable content
- Full-screen view option

#### Column Information
Click "📝 Column Information" to see:
- Data types
- Non-null counts
- Unique value counts
- Missing value counts

#### Data Validation
1. Click "🔍 Run Data Validation"
2. Wait for validation to complete
3. Review validation report:
   - Overall status (Pass/Fail)
   - Individual check results
   - Detailed messages

### Step 3: Filter Data (Filter & Export Tab)

#### Configure Filters

All filters are in the **sidebar**:

**Entity Type Filter**
1. Check "Enable Entity Type Filter"
2. Select entity types from dropdown
3. Multiple selections allowed

**Status Filter**
1. Check "Enable Status Filter"
2. Choose statuses (Active, Suspended, etc.)
3. Default: Active

**Date Range Filter**
1. Check "Enable Date Range Filter"
2. Set start date using calendar
3. Set end date using calendar
4. Filters registration dates

**Location Filter**
1. Check "Enable Location Filter"
2. Select cities from dropdown
3. Shows top 50 most common cities
4. Multiple selections allowed

**Name Pattern Filter**
1. Check "Enable Name Pattern Filter"
2. Enter pattern (supports regex)
3. Examples:
   - `.*Tech.*` - Contains "Tech"
   - `.*LLC.*` - Contains "LLC"
   - `^ABC.*` - Starts with "ABC"

**Output Settings**
1. Check "Limit Output Records"
2. Enter maximum number of records
3. Useful for large datasets

#### Apply Filters

1. Configure desired filters (see above)
2. Click "▶ Apply Filters" button
3. Wait for processing
4. View results summary:
   - Original record count
   - Filtered record count
   - Retention rate percentage

#### Preview Filtered Data

- Filtered data appears below the button
- First 100 rows shown
- Full interactive table
- Sortable and searchable

#### Download Results

Three download options:

**CSV Format**
- Click "📥 Download CSV"
- Opens in Excel, Google Sheets, etc.
- Best for further analysis
- Smallest file size

**JSON Format**
- Click "📥 Download JSON"
- Structured data format
- Best for APIs and programming
- Human-readable

**Excel Format**
- Click "📥 Download Excel"
- Native Excel file (.xlsx)
- Best for business users
- Formatted and ready to use

All downloads include timestamp in filename.

### Step 4: Visualizations (Visualizations Tab)

Choose data source:
- **Original Data**: Charts from uploaded data
- **Filtered Data**: Charts from filtered results

#### Available Charts

**Entity Type Distribution**
- Bar chart showing business types
- Top 10 most common types
- Color-coded by count

**Status Distribution**
- Pie chart with donut hole
- Shows proportion of each status
- Interactive hover details

**Top Cities**
- Horizontal bar chart
- Top 15 cities by business count
- Sorted by volume

**Registration Timeline**
- Line chart over time
- Grouped by month
- Shows growth trends
- Interactive zoom and pan

All charts are:
- **Interactive**: Hover for details
- **Zoomable**: Click and drag
- **Exportable**: Download as PNG

### Step 5: About Tab

Reference information:
- Tool overview
- Feature list
- Data sources
- Quick start guide
- Documentation links

## Tips and Best Practices

### Performance

**Large Files (> 100MB)**
- Upload may take 30-60 seconds
- Use "Limit Output Records" to improve speed
- Apply restrictive filters first

**Very Large Files (> 1GB)**
- Consider using CLI instead: `python -m src.cli --chunk-size 50000`
- Web UI may timeout or run out of memory

### Workflow Recommendations

**For Exploration**
1. Load sample data first
2. Experiment with filters
3. Review visualizations
4. Then load real data

**For Production**
1. Load your data file
2. Run validation first
3. Configure and test filters
4. Review filtered data preview
5. Download results

**For Repeated Tasks**
1. Note your filter settings
2. Create a custom `filters.yaml` file
3. Use CLI for automation:
   ```bash
   python -m src.cli --input data.csv --config my_filters.yaml
   ```

### Filter Combinations

**Find Active Tech Companies in SF**
```
✓ Enable Entity Type Filter
  - Select: DOMESTIC LIMITED LIABILITY COMPANY
✓ Enable Status Filter
  - Select: ACTIVE
✓ Enable Location Filter
  - Select: San Francisco
✓ Enable Name Pattern Filter
  - Pattern: .*Tech.*|.*Software.*
```

**Recent Registrations**
```
✓ Enable Date Range Filter
  - Start: 2024-01-01
  - End: 2024-12-31
✓ Enable Status Filter
  - Select: ACTIVE
```

## Keyboard Shortcuts

When using the web UI:

- **Ctrl + R**: Refresh page
- **Ctrl + K**: Open command palette (Streamlit)
- **Ctrl + Shift + R**: Hard refresh
- **Ctrl + F**: Search within tables

## Troubleshooting

### Problem: Web UI Won't Start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install streamlit plotly
```

### Problem: File Upload Fails

**Symptom:** Error message after clicking "Load Data"

**Solutions:**
1. Check file format (must be CSV or ZIP)
2. Verify file isn't corrupted
3. Try smaller file first
4. Check file encoding (UTF-8 recommended)

### Problem: Charts Don't Display

**Symptom:** Empty visualization tab

**Solutions:**
1. Ensure data has expected columns
2. Column names must match patterns:
   - Entity Type: ENTITY_TYPE, EntityType, Type
   - Status: STATUS, Status
   - City: CITY, City
3. Check for null values in chart columns

### Problem: Slow Performance

**Symptoms:**
- Long load times
- Laggy interface
- Timeout errors

**Solutions:**
1. Use "Limit Output Records"
2. Apply more restrictive filters
3. Use CLI for very large files:
   ```bash
   python -m src.cli --input large_file.csv --chunk-size 50000
   ```

### Problem: Download Button Doesn't Work

**Symptom:** Click download but nothing happens

**Solutions:**
1. Check browser pop-up blocker
2. Ensure filtered data exists (apply filters first)
3. Try different download format
4. Check browser console for errors (F12)

### Problem: Filters Not Working

**Symptom:** Same results before/after filtering

**Solutions:**
1. Verify filters are **enabled** (checkbox checked)
2. Ensure filter values are selected
3. Check column names match your data
4. Click "▶ Apply Filters" button

## Advanced Features

### Custom Styling

The web UI uses custom CSS for professional appearance. You can modify `app.py` to change colors, fonts, and layout.

### Session State

The app maintains state during your session:
- Loaded data persists across tabs
- Filter settings remembered
- Validation results cached

To clear and start fresh: Refresh the page (Ctrl + R)

### URL Parameters

Access specific views directly:

```
http://localhost:8501/?tab=overview
http://localhost:8501/?tab=filter
http://localhost:8501/?tab=viz
```

(Note: Requires custom implementation)

## Mobile Usage

The web UI is **responsive** and works on mobile:
- Tablets: Full functionality
- Phones: Limited (sidebar becomes menu)
- Best on desktop/laptop

## Security Notes

- **Local Only**: Default runs on localhost (not accessible remotely)
- **No Authentication**: Anyone with local access can use
- **Data Privacy**: Data never leaves your machine
- **No Cloud**: Everything processed locally

To enable remote access (use with caution):
```bash
streamlit run app.py --server.address 0.0.0.0
```

## Comparison: Web UI vs CLI

| Feature | Web UI | CLI |
|---------|--------|-----|
| Ease of Use | ⭐⭐⭐⭐⭐ Very Easy | ⭐⭐⭐ Moderate |
| Speed | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Fastest |
| Large Files | ⭐⭐⭐ Limited | ⭐⭐⭐⭐⭐ Excellent |
| Visualizations | ⭐⭐⭐⭐⭐ Built-in | ⭐ None |
| Automation | ⭐ Manual | ⭐⭐⭐⭐⭐ Scriptable |
| Batch Processing | ⭐ One at a time | ⭐⭐⭐⭐⭐ Multiple |

**Recommendation:**
- **Exploration & Analysis**: Use Web UI
- **Production & Automation**: Use CLI
- **Large Datasets**: Use CLI with chunking

## FAQ

**Q: Can I use the web UI and CLI together?**

A: Yes! They use the same backend modules. Configure filters in the UI, note the settings, then use CLI for automation.

**Q: Where are my downloads saved?**

A: Browser's default download folder (usually `~/Downloads`)

**Q: Can I save my filter configuration?**

A: Not directly in the UI. Note your settings and create a `filters.yaml` file for CLI use.

**Q: How do I process multiple files?**

A: The web UI processes one file at a time. For batch processing, use the CLI:
```bash
python -m src.cli --input-dir ./data --config filters.yaml
```

**Q: Can I export the charts?**

A: Yes! Hover over any chart and click the camera icon to download as PNG.

**Q: What browsers are supported?**

A: Chrome, Firefox, Safari, Edge (modern versions). Chrome recommended for best experience.

**Q: Can I customize the UI?**

A: Yes! Edit `app.py` to modify layout, colors, and features. Basic Python/Streamlit knowledge required.

## Getting Help

If you encounter issues:

1. **Check this guide** for solutions
2. **Review README.md** for general info
3. **Check logs** in terminal/console
4. **Try CLI instead** for comparison
5. **Restart the app** (Ctrl+C, then restart)

## Next Steps

After mastering the web UI:

1. **Explore CLI**: For automation and large files
2. **Read USAGE_EXAMPLES.md**: 23 detailed examples
3. **Customize filters.yaml**: Create reusable configurations
4. **Integrate into workflow**: Combine with other tools

---

**Web UI Version**: 1.0.0
**Last Updated**: 2025-11-16
**Powered by**: Streamlit, Plotly, Pandas
