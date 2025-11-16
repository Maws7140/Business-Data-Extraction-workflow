"""
Data Filtering Module
Applies various filters to business entity data
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd


class DataFilter:
    """
    Filters business entity data based on various criteria
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DataFilter with configuration

        Args:
            config: Filter configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all enabled filters to the DataFrame

        Args:
            df: Input DataFrame

        Returns:
            Filtered DataFrame
        """
        original_count = len(df)
        self.logger.info(f"Starting with {original_count} records")

        filtered_df = df.copy()

        filters_config = self.config.get('filters', {})

        # Apply entity type filter
        if filters_config.get('entity_types', {}).get('enabled', False):
            filtered_df = self._filter_entity_types(filtered_df, filters_config['entity_types'])

        # Apply status filter
        if filters_config.get('status', {}).get('enabled', False):
            filtered_df = self._filter_status(filtered_df, filters_config['status'])

        # Apply registration date filter
        if filters_config.get('registration_date', {}).get('enabled', False):
            filtered_df = self._filter_date_range(filtered_df, filters_config['registration_date'])

        # Apply location filter
        if filters_config.get('location', {}).get('enabled', False):
            filtered_df = self._filter_location(filtered_df, filters_config['location'])

        # Apply name pattern filter
        if filters_config.get('name_patterns', {}).get('enabled', False):
            filtered_df = self._filter_name_patterns(filtered_df, filters_config['name_patterns'])

        # Apply agent filter
        if filters_config.get('agent', {}).get('enabled', False):
            filtered_df = self._filter_agent(filtered_df, filters_config['agent'])

        # Apply custom filters
        if filters_config.get('custom_filters', {}).get('enabled', False):
            filtered_df = self._filter_custom(filtered_df, filters_config['custom_filters'])

        final_count = len(filtered_df)
        removed_count = original_count - final_count
        self.logger.info(f"Filtering complete: {final_count} records remaining ({removed_count} removed)")

        return filtered_df

    def _filter_entity_types(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Filter by entity types"""
        entity_types = config.get('values', [])

        if not entity_types:
            return df

        # Try common column names for entity type
        possible_columns = ['ENTITY_TYPE', 'EntityType', 'Type', 'BUSINESS_TYPE']
        column = self._find_column(df, possible_columns)

        if column:
            mask = df[column].isin(entity_types)
            filtered = df[mask]
            self.logger.info(f"Entity type filter: {len(filtered)} records match {entity_types}")
            return filtered
        else:
            self.logger.warning("Entity type column not found, skipping entity type filter")
            return df

    def _filter_status(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Filter by status"""
        statuses = config.get('values', [])

        if not statuses:
            return df

        possible_columns = ['STATUS', 'Status', 'ENTITY_STATUS', 'EntityStatus']
        column = self._find_column(df, possible_columns)

        if column:
            mask = df[column].isin(statuses)
            filtered = df[mask]
            self.logger.info(f"Status filter: {len(filtered)} records match {statuses}")
            return filtered
        else:
            self.logger.warning("Status column not found, skipping status filter")
            return df

    def _filter_date_range(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Filter by date range"""
        start_date = config.get('start_date')
        end_date = config.get('end_date')

        possible_columns = ['REGISTRATION_DATE', 'RegistrationDate', 'FILE_DATE', 'FileDate', 'DATE']
        column = self._find_column(df, possible_columns)

        if column:
            # Convert to datetime
            df[column] = pd.to_datetime(df[column], errors='coerce')

            mask = pd.Series([True] * len(df))

            if start_date:
                start = pd.to_datetime(start_date)
                mask &= df[column] >= start

            if end_date:
                end = pd.to_datetime(end_date)
                mask &= df[column] <= end

            filtered = df[mask]
            self.logger.info(f"Date range filter: {len(filtered)} records between {start_date} and {end_date}")
            return filtered
        else:
            self.logger.warning("Date column not found, skipping date filter")
            return df

    def _filter_location(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Filter by location (city, county, zip)"""
        cities = config.get('cities', [])
        counties = config.get('counties', [])
        zip_codes = config.get('zip_codes', [])

        mask = pd.Series([True] * len(df))

        if cities:
            city_columns = ['CITY', 'City', 'PRINCIPAL_CITY', 'PrincipalCity']
            city_col = self._find_column(df, city_columns)
            if city_col:
                mask &= df[city_col].isin(cities)

        if counties:
            county_columns = ['COUNTY', 'County']
            county_col = self._find_column(df, county_columns)
            if county_col:
                mask &= df[county_col].isin(counties)

        if zip_codes:
            zip_columns = ['ZIP', 'ZIP_CODE', 'ZipCode', 'POSTAL_CODE']
            zip_col = self._find_column(df, zip_columns)
            if zip_col:
                # Convert zip codes to string for comparison
                df[zip_col] = df[zip_col].astype(str)
                zip_codes_str = [str(z) for z in zip_codes]
                mask &= df[zip_col].isin(zip_codes_str)

        filtered = df[mask]
        self.logger.info(f"Location filter: {len(filtered)} records match location criteria")
        return filtered

    def _filter_name_patterns(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Filter by name patterns (regex)"""
        patterns = config.get('patterns', [])

        if not patterns:
            return df

        name_columns = ['ENTITY_NAME', 'EntityName', 'NAME', 'Name', 'BUSINESS_NAME']
        column = self._find_column(df, name_columns)

        if column:
            # Combine patterns with OR
            combined_pattern = '|'.join(patterns)
            mask = df[column].str.contains(combined_pattern, case=False, na=False, regex=True)
            filtered = df[mask]
            self.logger.info(f"Name pattern filter: {len(filtered)} records match patterns")
            return filtered
        else:
            self.logger.warning("Name column not found, skipping name pattern filter")
            return df

    def _filter_agent(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Filter by agent names"""
        agent_names = config.get('agent_names', [])

        if not agent_names:
            return df

        agent_columns = ['AGENT_NAME', 'AgentName', 'REGISTERED_AGENT', 'RegisteredAgent']
        column = self._find_column(df, agent_columns)

        if column:
            mask = df[column].isin(agent_names)
            filtered = df[mask]
            self.logger.info(f"Agent filter: {len(filtered)} records match agent criteria")
            return filtered
        else:
            self.logger.warning("Agent column not found, skipping agent filter")
            return df

    def _filter_custom(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Apply custom field filters"""
        mask = pd.Series([True] * len(df))

        for field, values in config.items():
            if field == 'enabled':
                continue

            if field in df.columns and values:
                mask &= df[field].isin(values)
                self.logger.info(f"Custom filter on {field}: filtering by {values}")

        return df[mask]

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """
        Find a column in DataFrame from a list of possible names

        Args:
            df: DataFrame to search
            possible_names: List of possible column names

        Returns:
            Column name if found, None otherwise
        """
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    def apply_output_limits(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply output configuration limits

        Args:
            df: Input DataFrame

        Returns:
            Limited DataFrame
        """
        output_config = self.config.get('output', {})
        max_records = output_config.get('max_records')

        if max_records and max_records > 0:
            df = df.head(max_records)
            self.logger.info(f"Limited output to {max_records} records")

        return df
