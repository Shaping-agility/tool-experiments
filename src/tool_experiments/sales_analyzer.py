from pathlib import Path
from typing import Optional, Any
from datetime import date
import pandas as pd
from .spreadsheet_manager import SpreadsheetManager


class SalesAnalyzer:
    """Analyzes confirmed sales data from Excel spreadsheets."""
    
    def __init__(self, file_path: Optional[Path] = None):
        """Initialize the SalesAnalyzer.
        
        Args:
            file_path: Path to the business spreadsheet. Defaults to data/raw/Business.xlsm
        """
        if file_path is None:
            self.file_path = Path("data/raw/Business.xlsm")
        else:
            self.file_path = Path(file_path)
        
        self.spreadsheet_manager = SpreadsheetManager(self.file_path)
        self._is_open = False
        
        # Configuration for different sheet types
        self._sheet_configs = {
            'industry': {
                'sheet_name': 'LD-Business',
                'required_columns': [0, 3, 8, 16, 25, 18],  # A, D, I, Q, Z, S (0-indexed)
                'column_names': ['Client', 'Category', 'Product', 'Date', 'Total', 'Description']
            },
            'government': {
                'sheet_name': 'LG-Business',
                'required_columns': [0, 3, 8, 15, 24, 17],  # A, D, I, P, Y, R (0-indexed)
                'column_names': ['Client', 'Category', 'Product', 'Date', 'Total', 'Description']
            }
        }
        
        # Cache for loaded data
        self._cached_data: dict[str, dict[str, Any]] = {
            'industry': {
                'data': None,
                'date_from': None,
                'date_to': None
            },
            'government': {
                'data': None,
                'date_from': None,
                'date_to': None
            }
        }
    
    def _validate_date_range(self, start_date: date, end_date: date):
        """Validate that the date range is valid.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Raises:
            ValueError: If date range is invalid
        """
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")
    
    def _validate_sheet_exists(self, sheet_name: str):
        """Validate that a sheet exists in the workbook.
        
        Args:
            sheet_name: Name of the sheet to validate
            
        Raises:
            RuntimeError: If the sheet doesn't exist
        """
        if not self._is_open:
            self.spreadsheet_manager.open()
            self._is_open = True
        
        sheet_names = self.spreadsheet_manager.get_sheet_names()
        if sheet_name not in sheet_names:
            raise RuntimeError(f"Sheet '{sheet_name}' not found. Available sheets: {sheet_names}")
    
    def _ensureUnderlyingDataLoaded(self, config_key: str, start_date: date, end_date: date) -> pd.DataFrame:
        """Ensure that the underlying data for the specified config is loaded and covers the requested date range.
        
        Args:
            config_key: Key to identify the sheet configuration ('industry' or 'government')
            start_date: Start date for the required range
            end_date: End date for the required range
            
        Returns:
            pandas DataFrame with the cached data (or newly loaded if needed)
        """
        # Validate date range first
        self._validate_date_range(start_date, end_date)
        
        if config_key not in self._cached_data:
            raise ValueError(f"Unknown config key: {config_key}. Available keys: {list(self._cached_data.keys())}")
        
        cache = self._cached_data[config_key]
        
        # Check if we have cached data that covers the requested range
        if (cache['data'] is not None and 
            cache['date_from'] is not None and 
            cache['date_to'] is not None and
            cache['date_from'] <= start_date and 
            cache['date_to'] >= end_date):
            # Cached data covers the requested range, filter it to the exact range requested
            cached_data = cache['data'].copy()
            
            # Apply date filtering to the cached data
            mask = (cached_data['Date'] >= pd.Timestamp(start_date)) & (cached_data['Date'] <= pd.Timestamp(end_date))
            filtered_data = cached_data[mask].copy()
            
            return filtered_data
        
        # Need to load new data
        new_data = self._get_sales_data(config_key, start_date, end_date)
        
        # Update cache
        cache['data'] = new_data
        cache['date_from'] = start_date
        cache['date_to'] = end_date
        
        return new_data
    
    def _get_sales_data(self, config_key: str, start_date: date, end_date: date) -> pd.DataFrame:
        """Get sales data from a specified sheet configuration.
        
        Args:
            config_key: Key to identify the sheet configuration ('industry' or 'government')
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            
        Returns:
            pandas DataFrame with standardized columns
            
        Raises:
            ValueError: If date range is invalid
            RuntimeError: If sheet doesn't exist or data can't be loaded
        """
        # Validate date range
        self._validate_date_range(start_date, end_date)
        
        # Get configuration
        if config_key not in self._sheet_configs:
            raise ValueError(f"Unknown config key: {config_key}. Available keys: {list(self._sheet_configs.keys())}")
        
        config = self._sheet_configs[config_key]
        sheet_name = config['sheet_name']
        required_columns = config['required_columns']
        column_names = config['column_names']
        
        # Validate sheet exists
        self._validate_sheet_exists(sheet_name)
        
        # Load data from the sheet with manual end column specification (Z)
        df = self.spreadsheet_manager.readRangeAsDataFrame(
            sheet_name=sheet_name,
            start_row=1,
            end_row=None,  # Auto-detect
            start_col="A",
            end_col="Z"
        )
        
        # Validate that required columns exist
        if len(df.columns) < max(required_columns) + 1:
            raise RuntimeError(f"Sheet '{sheet_name}' doesn't have enough columns. Expected at least {max(required_columns) + 1} columns, got {len(df.columns)}")
        
        # Select and rename the required columns
        selected_columns = df.iloc[:, required_columns].copy()
        selected_columns.columns = column_names
        
        # Convert Date column to datetime for filtering
        selected_columns['Date'] = pd.to_datetime(selected_columns['Date'], errors='coerce')
        
        # Filter by date range
        mask = (selected_columns['Date'] >= pd.Timestamp(start_date)) & (selected_columns['Date'] <= pd.Timestamp(end_date))
        filtered_df = selected_columns[mask].copy()
        
        # Reset index
        filtered_df = filtered_df.reset_index(drop=True)
        
        return filtered_df
    
    def getIndustrySalesData(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Get industry sales data from the LD-Business sheet.
        
        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            
        Returns:
            pandas DataFrame with columns: Client, Category, Product, Date, Total, Description
            
        Raises:
            ValueError: If date range is invalid
            RuntimeError: If sheet doesn't exist or data can't be loaded
        """
        return self._ensureUnderlyingDataLoaded('industry', start_date, end_date)
    
    def getGovSalesData(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Get government sales data from the LG-Business sheet.
        
        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            
        Returns:
            pandas DataFrame with columns: Client, Category, Product, Date, Total, Description
            
        Raises:
            ValueError: If date range is invalid
            RuntimeError: If sheet doesn't exist or data can't be loaded
        """
        return self._ensureUnderlyingDataLoaded('government', start_date, end_date)
    
    def getNewIndustryClients(self, start_date: date, end_date: date) -> list[str]:
        """Get list of unique industry clients for the specified date range.
        
        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            
        Returns:
            List of unique client names as strings
            
        Raises:
            ValueError: If date range is invalid
            RuntimeError: If sheet doesn't exist or data can't be loaded
        """
        # Ensure underlying data is loaded (uses caching)
        data = self._ensureUnderlyingDataLoaded('industry', start_date, end_date)
        
        # Get unique clients, excluding any None/NaN values
        unique_clients = data['Client'].dropna().unique().tolist()
        
        # Convert to strings and filter out empty strings
        client_list = [str(client).strip() for client in unique_clients if str(client).strip()]
        
        return client_list
    
    def getNewGovClients(self, start_date: date, end_date: date) -> list[str]:
        """Get list of unique government clients for the specified date range.
        
        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            
        Returns:
            List of unique client names as strings
            
        Raises:
            ValueError: If date range is invalid
            RuntimeError: If sheet doesn't exist or data can't be loaded
        """
        # Ensure underlying data is loaded (uses caching)
        data = self._ensureUnderlyingDataLoaded('government', start_date, end_date)
        
        # Get unique clients, excluding any None/NaN values
        unique_clients = data['Client'].dropna().unique().tolist()
        
        # Convert to strings and filter out empty strings
        client_list = [str(client).strip() for client in unique_clients if str(client).strip()]
        
        return client_list
    
    def close(self):
        """Close the spreadsheet connection."""
        if self._is_open and self.spreadsheet_manager.is_open:
            self.spreadsheet_manager.close()
        self._is_open = False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 