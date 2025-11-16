#!/usr/bin/env python3
"""
Web UI for Business Data Extraction Tool
Interactive Streamlit application for extracting and filtering business data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import tempfile
import zipfile
import io
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from extractor import DataExtractor
from filters import DataFilter
from validator import DataValidator


# Page configuration
st.set_page_config(
    page_title="Business Data Extraction Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = None
    if 'validation_report' not in st.session_state:
        st.session_state.validation_report = None


def load_data_from_file(uploaded_file):
    """Load data from uploaded file"""
    extractor = DataExtractor()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        file_path = tmp_path / uploaded_file.name

        # Save uploaded file
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Process file
        if file_path.suffix.lower() == '.zip':
            # Extract ZIP
            extracted_files = extractor.extract_zip(file_path, tmp_path)
            csv_files = [f for f in extracted_files if f.suffix.lower() == '.csv']
            if csv_files:
                df = extractor.read_multiple_csvs(csv_files)
            else:
                st.error("No CSV files found in ZIP archive")
                return None
        elif file_path.suffix.lower() == '.csv':
            # Read CSV
            df = extractor.read_csv(file_path)
        else:
            st.error("Unsupported file format. Please upload CSV or ZIP file.")
            return None

        return df


def create_filter_config(df):
    """Create filter configuration from sidebar inputs"""
    st.sidebar.header("🔍 Filter Configuration")

    config = {'filters': {}, 'output': {}}

    # Get column names for smart defaults
    columns = df.columns.tolist()

    # Helper function to find column
    def find_column(possible_names):
        for name in possible_names:
            if name in columns:
                return name
        return None

    # Entity Type Filter
    st.sidebar.subheader("Entity Type")
    entity_col = find_column(['ENTITY_TYPE', 'EntityType', 'Type', 'BUSINESS_TYPE'])
    if entity_col:
        unique_types = df[entity_col].dropna().unique().tolist()
        entity_filter_enabled = st.sidebar.checkbox("Enable Entity Type Filter", value=False)
        if entity_filter_enabled and unique_types:
            selected_types = st.sidebar.multiselect(
                "Select Entity Types",
                options=unique_types,
                default=unique_types[:3] if len(unique_types) >= 3 else unique_types
            )
            config['filters']['entity_types'] = {
                'enabled': True,
                'values': selected_types
            }

    # Status Filter
    st.sidebar.subheader("Status")
    status_col = find_column(['STATUS', 'Status', 'ENTITY_STATUS', 'EntityStatus'])
    if status_col:
        unique_statuses = df[status_col].dropna().unique().tolist()
        status_filter_enabled = st.sidebar.checkbox("Enable Status Filter", value=False)
        if status_filter_enabled and unique_statuses:
            selected_statuses = st.sidebar.multiselect(
                "Select Statuses",
                options=unique_statuses,
                default=['ACTIVE'] if 'ACTIVE' in unique_statuses else unique_statuses[:1]
            )
            config['filters']['status'] = {
                'enabled': True,
                'values': selected_statuses
            }

    # Date Range Filter
    st.sidebar.subheader("Registration Date")
    date_col = find_column(['REGISTRATION_DATE', 'RegistrationDate', 'FILE_DATE', 'FileDate', 'DATE'])
    if date_col:
        date_filter_enabled = st.sidebar.checkbox("Enable Date Range Filter", value=False)
        if date_filter_enabled:
            col1, col2 = st.sidebar.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=datetime(2020, 1, 1))
            with col2:
                end_date = st.date_input("End Date", value=datetime.now())

            config['filters']['registration_date'] = {
                'enabled': True,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }

    # Location Filter
    st.sidebar.subheader("Location")
    city_col = find_column(['CITY', 'City', 'PRINCIPAL_CITY', 'PrincipalCity'])
    if city_col:
        unique_cities = df[city_col].dropna().unique().tolist()
        location_filter_enabled = st.sidebar.checkbox("Enable Location Filter", value=False)
        if location_filter_enabled and unique_cities:
            selected_cities = st.sidebar.multiselect(
                "Select Cities",
                options=sorted(unique_cities)[:50],  # Limit to 50 for performance
                default=[]
            )
            if selected_cities:
                config['filters']['location'] = {
                    'enabled': True,
                    'cities': selected_cities,
                    'counties': [],
                    'zip_codes': []
                }

    # Name Pattern Filter
    st.sidebar.subheader("Name Pattern")
    name_filter_enabled = st.sidebar.checkbox("Enable Name Pattern Filter", value=False)
    if name_filter_enabled:
        pattern = st.sidebar.text_input(
            "Enter Pattern (regex supported)",
            placeholder="e.g., .*Tech.* or .*LLC.*"
        )
        if pattern:
            config['filters']['name_patterns'] = {
                'enabled': True,
                'patterns': [pattern]
            }

    # Output Limit
    st.sidebar.subheader("Output Settings")
    limit_output = st.sidebar.checkbox("Limit Output Records", value=False)
    if limit_output:
        max_records = st.sidebar.number_input(
            "Max Records",
            min_value=1,
            max_value=1000000,
            value=10000,
            step=1000
        )
        config['output']['max_records'] = max_records
    else:
        config['output']['max_records'] = None

    return config


def display_data_overview(df):
    """Display data overview with metrics and charts"""
    st.header("📊 Data Overview")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", f"{len(df):,}")

    with col2:
        st.metric("Columns", len(df.columns))

    with col3:
        null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        st.metric("Null Values", f"{null_percentage:.2f}%")

    with col4:
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("Memory Usage", f"{memory_mb:.2f} MB")

    # Data Preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(100), use_container_width=True)

    # Column Information
    with st.expander("📝 Column Information"):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.astype(str),
            'Non-Null Count': df.count(),
            'Null Count': df.isnull().sum(),
            'Unique Values': df.nunique()
        })
        st.dataframe(col_info, use_container_width=True)


def display_validation_results(validation_report):
    """Display validation results"""
    st.header("✅ Data Validation")

    if validation_report['is_valid']:
        st.success("✓ All validation checks passed!")
    else:
        st.warning("⚠ Some validation issues detected")

    # Summary metrics
    summary = validation_report['summary']
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Checks", summary['total_checks'])
    with col2:
        st.metric("Passed", summary['passed_checks'],
                 delta=f"{summary['success_rate']:.0f}%")
    with col3:
        st.metric("Failed", summary['failed_checks'])

    # Detailed results
    with st.expander("📊 Detailed Validation Results"):
        for name, validation in validation_report['validations'].items():
            status = "✓" if validation.get('passed', True) else "✗"
            st.write(f"{status} **{validation.get('name', name)}**: {validation.get('message', '')}")


def display_charts(df, title="Data Analysis"):
    """Display data visualizations"""
    st.header(f"📈 {title}")

    # Helper to find columns
    def find_column(possible_names):
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    col1, col2 = st.columns(2)

    # Chart 1: Entity Type Distribution
    with col1:
        entity_col = find_column(['ENTITY_TYPE', 'EntityType', 'Type', 'BUSINESS_TYPE'])
        if entity_col and entity_col in df.columns:
            st.subheader("Entity Type Distribution")
            type_counts = df[entity_col].value_counts().head(10)
            fig = px.bar(
                x=type_counts.index,
                y=type_counts.values,
                labels={'x': 'Entity Type', 'y': 'Count'},
                color=type_counts.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Chart 2: Status Distribution
    with col2:
        status_col = find_column(['STATUS', 'Status', 'ENTITY_STATUS', 'EntityStatus'])
        if status_col and status_col in df.columns:
            st.subheader("Status Distribution")
            status_counts = df[status_col].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Chart 3: Top Cities
    city_col = find_column(['CITY', 'City', 'PRINCIPAL_CITY', 'PrincipalCity'])
    if city_col and city_col in df.columns:
        st.subheader("Top 15 Cities by Business Count")
        city_counts = df[city_col].value_counts().head(15)
        fig = px.bar(
            x=city_counts.values,
            y=city_counts.index,
            orientation='h',
            labels={'x': 'Count', 'y': 'City'},
            color=city_counts.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Chart 4: Registration Timeline (if date column exists)
    date_col = find_column(['REGISTRATION_DATE', 'RegistrationDate', 'FILE_DATE', 'FileDate', 'DATE'])
    if date_col and date_col in df.columns:
        st.subheader("Registration Timeline")
        try:
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col])

            if len(df_temp) > 0:
                # Group by month
                df_temp['YearMonth'] = df_temp[date_col].dt.to_period('M').astype(str)
                timeline = df_temp.groupby('YearMonth').size().reset_index(name='Count')

                fig = px.line(
                    timeline,
                    x='YearMonth',
                    y='Count',
                    markers=True,
                    labels={'YearMonth': 'Month', 'Count': 'Registrations'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info(f"Could not create timeline chart: {e}")


def main():
    """Main application"""
    initialize_session_state()

    # Header
    st.markdown('<div class="main-header">📊 Business Data Extraction Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Extract and filter California Secretary of State business data</div>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("🎛 Control Panel")

    # File Upload
    st.sidebar.header("📁 Data Source")
    upload_option = st.sidebar.radio(
        "Choose data source:",
        ["Upload File", "Use Sample Data"]
    )

    uploaded_file = None

    if upload_option == "Upload File":
        uploaded_file = st.sidebar.file_uploader(
            "Upload CSV or ZIP file",
            type=['csv', 'zip'],
            help="Upload a CSV file or ZIP archive containing CSV files"
        )
    else:
        # Use sample data
        sample_path = Path("input/sample_data.csv")
        if sample_path.exists():
            st.sidebar.success("✓ Sample data available")
            if st.sidebar.button("Load Sample Data"):
                try:
                    extractor = DataExtractor()
                    st.session_state.df = extractor.read_csv(sample_path)
                    st.session_state.data_loaded = True
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error loading sample data: {e}")
        else:
            st.sidebar.warning("Sample data not found at input/sample_data.csv")

    # Process uploaded file
    if uploaded_file is not None:
        if st.sidebar.button("📥 Load Data"):
            with st.spinner("Loading data..."):
                try:
                    df = load_data_from_file(uploaded_file)
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.data_loaded = True
                        st.success(f"✓ Loaded {len(df):,} records with {len(df.columns)} columns")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error loading file: {e}")

    # Main content
    if st.session_state.data_loaded and st.session_state.df is not None:
        df = st.session_state.df

        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Filter & Export", "📈 Visualizations", "ℹ About"])

        with tab1:
            # Display overview
            display_data_overview(df)

            # Validation
            if st.button("🔍 Run Data Validation"):
                with st.spinner("Validating data..."):
                    validator = DataValidator()
                    is_valid, report = validator.validate(df)
                    st.session_state.validation_report = report

            if st.session_state.validation_report:
                display_validation_results(st.session_state.validation_report)

        with tab2:
            st.header("🔍 Filter and Export Data")

            # Create filter configuration
            filter_config = create_filter_config(df)

            # Apply filters button
            if st.button("▶ Apply Filters", type="primary"):
                with st.spinner("Applying filters..."):
                    try:
                        data_filter = DataFilter(filter_config)
                        filtered_df = data_filter.apply_filters(df)
                        filtered_df = data_filter.apply_output_limits(filtered_df)
                        st.session_state.filtered_df = filtered_df

                        # Show results
                        st.success(f"✓ Filtered {len(df):,} → {len(filtered_df):,} records")

                        # Metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Original Records", f"{len(df):,}")
                        with col2:
                            st.metric("Filtered Records", f"{len(filtered_df):,}")
                        with col3:
                            retention = (len(filtered_df) / len(df) * 100) if len(df) > 0 else 0
                            st.metric("Retention Rate", f"{retention:.1f}%")

                    except Exception as e:
                        st.error(f"Error applying filters: {e}")

            # Display filtered data
            if st.session_state.filtered_df is not None:
                filtered_df = st.session_state.filtered_df

                st.subheader("📋 Filtered Data Preview")
                st.dataframe(filtered_df.head(100), use_container_width=True)

                # Download options
                st.subheader("💾 Download Filtered Data")

                col1, col2, col3 = st.columns(3)

                with col1:
                    # CSV Download
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

                with col2:
                    # JSON Download
                    json_str = filtered_df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

                with col3:
                    # Excel Download
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        filtered_df.to_excel(writer, index=False, sheet_name='Filtered Data')

                    st.download_button(
                        label="📥 Download Excel",
                        data=buffer.getvalue(),
                        file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        with tab3:
            # Visualizations
            viz_option = st.radio(
                "Select data to visualize:",
                ["Original Data", "Filtered Data"] if st.session_state.filtered_df is not None else ["Original Data"]
            )

            if viz_option == "Filtered Data" and st.session_state.filtered_df is not None:
                display_charts(st.session_state.filtered_df, "Filtered Data Analysis")
            else:
                display_charts(df, "Original Data Analysis")

        with tab4:
            st.header("ℹ About This Tool")

            st.markdown("""
            ### Business Data Extraction Tool

            A comprehensive automation tool for extracting and filtering public business
            registration data from the California Secretary of State.

            #### Features

            - **Data Extraction**: Process CSV and ZIP files
            - **Flexible Filtering**: Filter by entity type, status, location, dates, and more
            - **Data Validation**: Comprehensive integrity checks
            - **Multiple Formats**: Export to CSV, JSON, or Excel
            - **Interactive Visualizations**: Charts and graphs for data analysis

            #### Data Sources

            This tool works with bulk data from the California Secretary of State:
            - Visit: https://www.sos.ca.gov/business-programs/bizfile
            - Download bulk business entity data
            - Upload to this tool for processing

            #### Quick Start

            1. Upload a CSV or ZIP file (or use sample data)
            2. Review data overview and validation
            3. Configure filters in the sidebar
            4. Apply filters and preview results
            5. Download filtered data in your preferred format

            #### Documentation

            - **README.md**: Complete usage guide
            - **SETUP.md**: Installation instructions
            - **USAGE_EXAMPLES.md**: Code examples

            #### Version

            Version 1.0.0 with Web UI

            ---

            Made with ❤️ using Streamlit and Python
            """)

    else:
        # Welcome screen
        st.info("👆 Upload a data file or load sample data to get started")

        st.markdown("""
        ### Welcome to the Business Data Extraction Tool

        This tool helps you extract and filter California Secretary of State business entity data.

        #### Getting Started

        1. **Upload Data**: Click "Browse files" in the sidebar to upload a CSV or ZIP file
        2. **Or Use Sample**: Select "Use Sample Data" to try the tool with example data
        3. **Explore**: View data overview, apply filters, and download results

        #### Supported File Formats

        - CSV files (.csv)
        - ZIP archives containing CSV files (.zip)

        #### Key Features

        - 📊 Interactive data preview
        - 🔍 Advanced filtering options
        - ✅ Data validation
        - 📈 Visual analytics
        - 💾 Multi-format export (CSV, JSON, Excel)
        """)


if __name__ == '__main__':
    main()
