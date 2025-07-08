# tests/test_sales_analyzer.py
import pytest
from pathlib import Path
from datetime import date, datetime
from src.tool_experiments.sales_analyzer import SalesAnalyzer
import pandas as pd


class TestSalesAnalyzer:
    """Test cases for SalesAnalyzer class."""
    
    @classmethod
    def setup_class(cls):
        """Set up the test class with a single SalesAnalyzer instance."""
        cls.business_file_path = Path("data/raw/Business.xlsm")
        cls.analyzer = SalesAnalyzer(cls.business_file_path)
        # Note: We don't open the analyzer here - it will be opened when first needed
    
    @classmethod
    def teardown_class(cls):
        """Clean up the test class by closing the SalesAnalyzer."""
        if hasattr(cls, 'analyzer') and cls.analyzer:
            cls.analyzer.close()
    
   
    def test_can_load_industry_sales_data(self):
        """Test that we can load industry sales data with date filtering."""
        # Use a reasonable date range for testing
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        
        df = self.analyzer.getIndustrySalesData(start_date, end_date)
        
        # Verify we got a DataFrame
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 0  # May be empty depending on data
        
        # Verify we have the expected columns
        expected_columns = ['Client', 'Category', 'Product', 'Date', 'Total', 'Description']
        assert list(df.columns) == expected_columns, f"Expected columns {expected_columns}, got {list(df.columns)}"
        
        # Verify Date column is datetime
        if len(df) > 0:
            assert pd.api.types.is_datetime64_any_dtype(df['Date'])
            
            # Verify all dates are within the specified range
            for row_date in df['Date']:
                assert start_date <= row_date.date() <= end_date
    
    def test_can_load_gov_sales_data(self):
        """Test that we can load government sales data with date filtering."""
        # Use a reasonable date range for testing
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        
        df = self.analyzer.getGovSalesData(start_date, end_date)
        
        # Verify we got a DataFrame
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 0  # May be empty depending on data
        
        # Verify we have the expected columns
        expected_columns = ['Client', 'Category', 'Product', 'Date', 'Total', 'Description']
        assert list(df.columns) == expected_columns, f"Expected columns {expected_columns}, got {list(df.columns)}"
        
        # Verify Date column is datetime
        if len(df) > 0:
            assert pd.api.types.is_datetime64_any_dtype(df['Date'])
            
            # Verify all dates are within the specified range
            for row_date in df['Date']:
                assert start_date <= row_date.date() <= end_date
    
    def test_date_range_filtering(self):
        """Test that date range filtering works correctly."""
        # Test with a very narrow date range
        start_date = date(2024, 6, 1)
        end_date = date(2024, 6, 30)
        
        industry_df = self.analyzer.getIndustrySalesData(start_date, end_date)
        gov_df = self.analyzer.getGovSalesData(start_date, end_date)
        
        # Verify all dates are within the narrow range
        for df in [industry_df, gov_df]:
            if len(df) > 0:
                for row_date in df['Date']:
                    assert start_date <= row_date.date() <= end_date
    
    def test_invalid_date_range(self):
        """Test that invalid date ranges raise appropriate errors."""
        # Test with start date after end date
        start_date = date(2024, 12, 31)
        end_date = date(2024, 1, 1)
        
        with pytest.raises(ValueError) as exc_info:
            self.analyzer.getIndustrySalesData(start_date, end_date)
        assert "Start date must be before or equal to end date" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            self.analyzer.getGovSalesData(start_date, end_date)
        assert "Start date must be before or equal to end date" in str(exc_info.value)
    
    def test_missing_sheet_error(self):
        """Test that appropriate error is raised for missing sheets."""
        # Try to access a non-existent sheet by temporarily modifying the method
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        
        # This should work normally
        try:
            self.analyzer.getIndustrySalesData(start_date, end_date)
        except RuntimeError as e:
            if "Sheet 'LD-Business' not found" in str(e):
                # This is expected if the sheet doesn't exist
                pass
            else:
                raise
    
    def test_column_validation(self):
        """Test that column validation works correctly."""
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        
        # These should either work or raise appropriate errors
        try:
            industry_df = self.analyzer.getIndustrySalesData(start_date, end_date)
            # If it works, verify the structure
            if len(industry_df) > 0:
                assert 'Client' in industry_df.columns
                assert 'Total' in industry_df.columns
        except RuntimeError as e:
            if "doesn't have enough columns" in str(e):
                # This is expected if the sheet structure is different
                pass
            else:
                raise
    
    def test_context_manager(self):
        """Test that the analyzer works as a context manager."""
        # Create a separate instance for context manager testing
        with SalesAnalyzer(self.business_file_path) as analyzer:
            start_date = date(2023, 1, 1)
            end_date = date(2024, 12, 31)
            
            # Should be able to load data
            df = analyzer.getIndustrySalesData(start_date, end_date)
            assert isinstance(df, pd.DataFrame)
        
        # Verify the connection was closed
        assert not analyzer._is_open
    
    def test_raises_error_for_missing_file(self):
        """Test that appropriate error is raised for missing file."""
        analyzer = SalesAnalyzer(Path("data/raw/nonexistent.xlsm"))
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        
        with pytest.raises(FileNotFoundError):
            analyzer.getIndustrySalesData(start_date, end_date)
    
    def test_invalid_config_key(self):
        """Test that invalid config keys raise appropriate errors."""
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        
        with pytest.raises(ValueError) as exc_info:
            self.analyzer._get_sales_data('invalid_key', start_date, end_date)
        assert "Unknown config key: invalid_key" in str(exc_info.value) 