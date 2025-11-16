"""
Data Extractor Module
Handles extraction of business entity data from various sources
"""

import os
import csv
import json
import zipfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from io import StringIO, BytesIO
import pandas as pd
from tqdm import tqdm


class DataExtractor:
    """
    Extracts business entity data from CA Secretary of State sources
    Supports both bulk file downloads and local file processing
    """

    def __init__(self, input_dir: str = "./input", output_dir: str = "./output"):
        """
        Initialize the DataExtractor

        Args:
            input_dir: Directory containing input data files
            output_dir: Directory for output files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)

        # Create directories if they don't exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_bulk_data(self, url: str, output_filename: Optional[str] = None) -> Path:
        """
        Download bulk data file from a URL

        Args:
            url: URL to download data from
            output_filename: Optional custom filename for downloaded file

        Returns:
            Path to downloaded file
        """
        if output_filename is None:
            output_filename = url.split('/')[-1]

        output_path = self.input_dir / output_filename

        self.logger.info(f"Downloading bulk data from {url}")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        size = f.write(chunk)
                        pbar.update(size)

            self.logger.info(f"Download completed: {output_path}")
            return output_path

        except requests.RequestException as e:
            self.logger.error(f"Failed to download bulk data: {e}")
            raise

    def extract_zip(self, zip_path: Path, extract_dir: Optional[Path] = None) -> List[Path]:
        """
        Extract ZIP file and return paths to extracted files

        Args:
            zip_path: Path to ZIP file
            extract_dir: Optional directory to extract to (defaults to input_dir)

        Returns:
            List of paths to extracted files
        """
        if extract_dir is None:
            extract_dir = self.input_dir

        self.logger.info(f"Extracting {zip_path}")

        extracted_files = []

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                extracted_files = [extract_dir / name for name in zip_ref.namelist()]

            self.logger.info(f"Extracted {len(extracted_files)} files")
            return extracted_files

        except zipfile.BadZipFile as e:
            self.logger.error(f"Invalid ZIP file: {e}")
            raise

    def read_csv(self, file_path: Path, encoding: str = 'utf-8',
                 chunk_size: Optional[int] = None) -> pd.DataFrame:
        """
        Read CSV file into pandas DataFrame

        Args:
            file_path: Path to CSV file
            encoding: File encoding (default: utf-8)
            chunk_size: Optional chunk size for reading large files

        Returns:
            DataFrame containing the data
        """
        self.logger.info(f"Reading CSV file: {file_path}")

        try:
            if chunk_size:
                # Read in chunks for large files
                chunks = []
                for chunk in pd.read_csv(file_path, encoding=encoding, chunksize=chunk_size):
                    chunks.append(chunk)
                df = pd.concat(chunks, ignore_index=True)
            else:
                df = pd.read_csv(file_path, encoding=encoding, low_memory=False)

            self.logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
            return df

        except Exception as e:
            self.logger.error(f"Failed to read CSV file: {e}")
            raise

    def read_multiple_csvs(self, file_paths: List[Path],
                          encoding: str = 'utf-8') -> pd.DataFrame:
        """
        Read and combine multiple CSV files

        Args:
            file_paths: List of paths to CSV files
            encoding: File encoding

        Returns:
            Combined DataFrame
        """
        self.logger.info(f"Reading {len(file_paths)} CSV files")

        dataframes = []
        for file_path in file_paths:
            if file_path.suffix.lower() == '.csv':
                df = self.read_csv(file_path, encoding=encoding)
                dataframes.append(df)

        if not dataframes:
            raise ValueError("No valid CSV files found")

        combined_df = pd.concat(dataframes, ignore_index=True)
        self.logger.info(f"Combined total: {len(combined_df)} records")

        return combined_df

    def get_data_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get information about the dataset

        Args:
            df: DataFrame to analyze

        Returns:
            Dictionary with dataset information
        """
        info = {
            'total_records': len(df),
            'columns': list(df.columns),
            'column_count': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'null_counts': df.isnull().sum().to_dict(),
            'dtypes': df.dtypes.astype(str).to_dict()
        }

        return info

    def export_data(self, df: pd.DataFrame, filename: str,
                   format: str = 'csv', include_index: bool = False) -> Path:
        """
        Export DataFrame to file

        Args:
            df: DataFrame to export
            filename: Output filename (without extension)
            format: Output format ('csv', 'json', 'excel')
            include_index: Whether to include index in output

        Returns:
            Path to exported file
        """
        format = format.lower()

        if format == 'csv':
            output_path = self.output_dir / f"{filename}.csv"
            df.to_csv(output_path, index=include_index, encoding='utf-8')
        elif format == 'json':
            output_path = self.output_dir / f"{filename}.json"
            df.to_json(output_path, orient='records', indent=2)
        elif format == 'excel':
            output_path = self.output_dir / f"{filename}.xlsx"
            df.to_excel(output_path, index=include_index, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported format: {format}")

        self.logger.info(f"Exported {len(df)} records to {output_path}")
        return output_path
