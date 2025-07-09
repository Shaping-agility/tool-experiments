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
                'required_columns': [0, 3, 8, 16, 25, 18, 6, 7],  # A, D, I, Q, Z, S, G, H (0-indexed)
                'column_names': ['Client', 'Category', 'Product', 'Date', 'Total', 'Description', 'ClientStatus', 'Ongoing']
            },
            'government': {
                'sheet_name': 'LG-Business',
                'required_columns': [0, 3, 8, 15, 24, 17, 6, 7],  # A, D, I, P, Y, R, G, H (0-indexed)
                'column_names': ['Client', 'Category', 'Product', 'Date', 'Total', 'Description', 'ClientStatus', 'Ongoing']
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
        self._validate_date_range(start_date, end_date)
        if config_key not in self._cached_data:
            raise ValueError(f"Unknown config key: {config_key}. Available keys: {list(self._cached_data.keys())}")
        cache = self._cached_data[config_key]
        if self._cache_covers_range(cache, start_date, end_date):
            return self._filter_cached_data_by_date(cache['data'], start_date, end_date)
        new_data = self._get_sales_data(config_key, start_date, end_date)
        cache['data'] = new_data
        cache['date_from'] = start_date
        cache['date_to'] = end_date
        return new_data
    
    def _cache_covers_range(self, cache: dict, start_date: date, end_date: date) -> bool:
        """Check if the cache covers the requested date range."""
        return (
            cache['data'] is not None and 
            cache['date_from'] is not None and 
            cache['date_to'] is not None and
            cache['date_from'] <= start_date and 
            cache['date_to'] >= end_date
        )
    
    def _filter_cached_data_by_date(self, cached_data: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
        """Return a copy of cached_data filtered to the given date range as a DataFrame."""
        mask = (cached_data['Date'] >= pd.Timestamp(start_date)) & (cached_data['Date'] <= pd.Timestamp(end_date))
        filtered = cached_data[mask]
        if not isinstance(filtered, pd.DataFrame):
            filtered = filtered.to_frame().T if hasattr(filtered, 'to_frame') else pd.DataFrame([filtered])
        return filtered.copy().reset_index(drop=True)
    
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
        self._validate_date_range(start_date, end_date)
        if config_key not in self._sheet_configs:
            raise ValueError(f"Unknown config key: {config_key}. Available keys: {list(self._sheet_configs.keys())}")
        config = self._sheet_configs[config_key]
        sheet_name = config['sheet_name']
        required_columns = config['required_columns']
        column_names = config['column_names']
        self._validate_sheet_exists(sheet_name)
        df = self._read_sheet_as_dataframe(sheet_name)
        self._validate_required_columns(df, required_columns, sheet_name)
        selected_columns = self._select_and_rename_required_columns(df, required_columns, column_names)
        filtered_df = self._filter_result_by_date_range(selected_columns, start_date, end_date)
        return filtered_df
    
    def _read_sheet_as_dataframe(self, sheet_name: str) -> pd.DataFrame:
        """Read the specified sheet as a DataFrame, up to column Z."""
        return self.spreadsheet_manager.readRangeAsDataFrame(
            sheet_name=sheet_name,
            start_row=1,
            end_row=None,
            start_col="A",
            end_col="Z"
        )
    
    def _validate_required_columns(self, df: pd.DataFrame, required_columns: list, sheet_name: str):
        """Raise if the DataFrame does not have enough columns for the required indices."""
        if len(df.columns) < max(required_columns) + 1:
            raise RuntimeError(
                f"Sheet '{sheet_name}' doesn't have enough columns. Expected at least {max(required_columns) + 1} columns, got {len(df.columns)}"
            )
    
    def _select_and_rename_required_columns(self, df: pd.DataFrame, required_columns: list, column_names: list) -> pd.DataFrame:
        """Select and rename required columns, convert Date column to datetime, and trim string fields."""
        selected_columns = df.iloc[:, required_columns].copy()
        selected_columns.columns = column_names
        selected_columns['Date'] = pd.to_datetime(selected_columns['Date'], errors='coerce')
        
        # Trim whitespace from string columns
        string_columns = ['Client', 'Category', 'Product', 'Description', 'ClientStatus', 'Ongoing']
        for col in string_columns:
            if col in selected_columns.columns:
                selected_columns[col] = selected_columns[col].astype(str).str.strip()
        
        # Add derived columns
        selected_columns = self._add_derived_columns(selected_columns)
        
        return selected_columns
    
    def _add_derived_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived boolean columns ExistingClient and New based on ClientStatus and Ongoing fields."""
        # Handle missing values: missing ClientStatus = 'not existing', missing Ongoing = 'not no'
        client_status = df['ClientStatus'].fillna('').astype(str)
        ongoing = df['Ongoing'].fillna('').astype(str)
        
        # ExistingClient: True if ClientStatus is 'Existing' (case insensitive)
        df['ExistingClient'] = client_status.str.lower() == 'existing'
        
        # New: True if not existing client, OR if existing client with Ongoing = 'No'
        df['New'] = (~df['ExistingClient']) | (ongoing.str.lower() == 'no')
        
        return df
    
    def _filter_result_by_date_range(self, df: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
        """Filter DataFrame by date range and reset index, always returning a DataFrame."""
        mask = (df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] <= pd.Timestamp(end_date))
        filtered = df[mask]
        if not isinstance(filtered, pd.DataFrame):
            filtered = filtered.to_frame().T if hasattr(filtered, 'to_frame') else pd.DataFrame([filtered])
        return filtered.copy().reset_index(drop=True)
    
    def getIndustrySalesData(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Get industry sales data from the LD-Business sheet.
        
        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            
        Returns:
            pandas DataFrame with columns: Client, Category, Product, Date, Total, Description, 
            ClientStatus, Ongoing, ExistingClient, New
            
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
            pandas DataFrame with columns: Client, Category, Product, Date, Total, Description,
            ClientStatus, Ongoing, ExistingClient, New
            
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
        data = self._ensureUnderlyingDataLoaded('industry', start_date, end_date)
        return self._extract_unique_clients(data)
    
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
        data = self._ensureUnderlyingDataLoaded('government', start_date, end_date)
        return self._extract_unique_clients(data)
    
    def getClientSummary(self, client_name: str, client_type: str, start_date: date, end_date: date) -> dict:
        """Get a summary of sales data for a specific client (new business only).
        
        Args:
            client_name: Name of the client to summarize
            client_type: Type of client ('industry' or 'government')
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            
        Returns:
            Dictionary with keys: client, amount, products, details, sale_type
            
        Raises:
            ValueError: If date range is invalid or client_type is invalid
            RuntimeError: If sheet doesn't exist or data can't be loaded
        """
        if client_type not in ['industry', 'government']:
            raise ValueError(f"Invalid client_type: {client_type}. Must be 'industry' or 'government'")
        
        data = self._ensureUnderlyingDataLoaded(client_type, start_date, end_date)
        filtered_data = self._filter_data_by_client(data, client_name)
        # Apply new business filter to client data
        new_business_data = self._filter_new_business_only(filtered_data)
        
        # Determine sale type based on original client data (before new business filtering)
        sale_type = self._determine_sale_type_from_data(filtered_data)
        
        return {
            'client': client_name,
            'amount': self._calculate_client_total_amount(new_business_data),
            'products': self._extract_unique_products(new_business_data),
            'details': self._extract_unique_details(new_business_data),
            'sale_type': sale_type
        }
    
    def _filter_data_by_client(self, data: pd.DataFrame, client_name: str) -> pd.DataFrame:
        """Filter DataFrame to include only rows for the specified client."""
        filtered = data[data['Client'] == client_name]
        if not isinstance(filtered, pd.DataFrame):
            filtered = filtered.to_frame().T if hasattr(filtered, 'to_frame') else pd.DataFrame([filtered])
        return filtered.copy()
    
    def _calculate_client_total_amount(self, data: pd.DataFrame) -> float:
        """Calculate the total amount for the client."""
        return float(data['Total'].sum())
    
    def _extract_unique_products(self, data: pd.DataFrame) -> list[str]:
        """Extract unique, non-empty products, excluding 'Consulting' and applying product name translations."""
        products = data['Product'].dropna().unique().tolist()
        raw_products = [str(product).strip() for product in products 
                       if str(product).strip() and str(product).strip() != 'Consulting' 
                       and str(product).strip().lower() not in ['none', 'nan']]
        
        # Apply product name translations
        product_mappings = {
            'expert.id': 'Consulting',
            'views.id': 'Views', 
            'profile.id': 'Profile',
            'atlas.id': 'Atlas',
            'economy.id': 'Economy',
            'forecast.id': 'Forecast',
            'Forecast (SAFi)': 'Forecast'
        }
        
        translated_products = []
        for product in raw_products:
            translated_product = product_mappings.get(product, product)
            translated_products.append(translated_product)
        
        return translated_products
    
    def _extract_unique_details(self, data: pd.DataFrame) -> list[str]:
        """Extract unique, non-empty descriptions, cleansing newlines and extra spaces."""
        details = data['Description'].dropna().unique().tolist()
        cleansed = []
        for detail in details:
            if not isinstance(detail, str):
                detail = str(detail)
            # Remove newlines and extra spaces, then trim
            clean = ' '.join(detail.replace('\n', ' ').replace('\r', ' ').split())
            # Filter out empty strings and string representations of missing values
            if clean and clean.lower() not in ['none', 'nan', '']:
                cleansed.append(clean)
        return cleansed
    
    def _determine_sale_type_from_data(self, data: pd.DataFrame) -> str:
        """Determine sale type based on ExistingClient column.
        
        Args:
            data: DataFrame containing client data with ExistingClient column
            
        Returns:
            'New client' if ExistingClient is False, 'Upsell' if True
        """
        if data.empty:
            return 'New client'  # Default for empty data
        
        # Check if any row has ExistingClient=True
        existing_client_count = data['ExistingClient'].sum()
        if existing_client_count > 0:
            return 'Upsell'
        else:
            return 'New client'
    
    def _extract_unique_clients(self, data: pd.DataFrame) -> list[str]:
        """Extract unique, non-empty client names from the DataFrame, filtering for new business only."""
        # Filter for new business only (exclude ExistingClient=True AND New=False)
        new_business_data = self._filter_new_business_only(data)
        unique_clients = new_business_data['Client'].dropna().unique().tolist()
        return [str(client).strip() for client in unique_clients if str(client).strip()]
    
    def _filter_new_business_only(self, data: pd.DataFrame) -> pd.DataFrame:
        """Filter DataFrame to include only new business rows (exclude ExistingClient=True AND New=False)."""
        # Keep rows where: NOT (ExistingClient=True AND New=False)
        # This means: (ExistingClient=False) OR (New=True)
        mask = (~data['ExistingClient']) | (data['New'])
        filtered = data[mask]
        if not isinstance(filtered, pd.DataFrame):
            filtered = filtered.to_frame().T if hasattr(filtered, 'to_frame') else pd.DataFrame([filtered])
        return filtered.copy().reset_index(drop=True)
    
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
    
    def getClientSummaryMarkdown(self, client_type: str, start_date: date, end_date: date) -> str:
        """Generate a markdown table of client summaries for a given client type and date range.
        
        Args:
            client_type: Type of client ('industry' or 'government')
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            
        Returns:
            Markdown formatted string with client summary table
            
        Raises:
            ValueError: If date range is invalid or client_type is invalid
            RuntimeError: If sheet doesn't exist or data can't be loaded
        """
        if client_type not in ['industry', 'government']:
            raise ValueError(f"Invalid client_type: {client_type}. Must be 'industry' or 'government'")
        
        clients = self._get_clients_by_type(client_type, start_date, end_date)
        summaries = []
        
        for client_name in clients:
            summary = self.getClientSummary(client_name, client_type, start_date, end_date)
            summaries.append(summary)
        
        return self._format_markdown_table(client_type, start_date, end_date, summaries)
    
    def _get_clients_by_type(self, client_type: str, start_date: date, end_date: date) -> list[str]:
        """Get list of clients for the specified type and date range."""
        if client_type == 'industry':
            return self.getNewIndustryClients(start_date, end_date)
        else:
            return self.getNewGovClients(start_date, end_date)
    
    def _format_markdown_table(self, client_type: str, start_date: date, end_date: date, summaries: list[dict]) -> str:
        """Format client summaries as a markdown table."""
        title = f"# New {client_type.title()} Clients ({start_date} to {end_date})"
        
        if not summaries:
            return f"{title}\n\nNo clients found for the specified date range."
        
        # Build table header
        table_lines = [
            title,
            "",
            "| Client | Amount | Products | Details | Sale Type |",
            "|--------|--------|----------|---------|-----------|"
        ]
        
        # Build table rows
        for summary in summaries:
            client = summary['client']
            amount = self._format_currency(summary['amount'])
            products = self._format_products(summary['products'])
            details = self._format_details(summary['details'])
            sale_type = summary['sale_type']
            
            table_lines.append(f"| {client} | {amount} | {products} | {details} | {sale_type} |")
        
        return "\n".join(table_lines)
    
    def _format_currency(self, amount: float) -> str:
        """Format amount as currency with $ and commas."""
        return f"${amount:,.0f}"
    
    def _format_products(self, products: list[str]) -> str:
        """Format products as comma-separated string, empty string if no products."""
        if not products:
            return ""
        return ", ".join(products)
    
    def _format_details(self, details: list[str]) -> str:
        """Format details as concatenated sentences, empty string if no details."""
        if not details:
            return ""
        return " ".join(details) 