# tests/test_sales_lead_analyzer.py
import pytest
from pathlib import Path
from src.tool_experiments.sales_lead_analyzer import SalesLeadAnalyzer
import pandas as pd


class TestSalesLeadAnalyzer:
    """Test cases for SalesLeadAnalyzer class."""
    
    @pytest.fixture
    def leads_file_path(self):
        """Path to the leads spreadsheet in data/raw directory."""
        return Path("data/raw/Leads.xlsx")
    
    @pytest.fixture
    def analyzer(self, leads_file_path):
        """Create a SalesLeadAnalyzer instance for testing."""
        return SalesLeadAnalyzer(leads_file_path, sheet_name="All deals")
    
    def test_can_create_analyzer(self, leads_file_path):
        """Test that we can create a SalesLeadAnalyzer instance."""
        analyzer = SalesLeadAnalyzer(leads_file_path, sheet_name="All deals")
        assert analyzer is not None
        assert analyzer.file_path == leads_file_path
        assert analyzer._sheet_name == "All deals"
    
    def test_can_load_leads_spreadsheet(self, analyzer):
        """Test that we can open leads.xlsx and load the 'All deals' sheet as DataFrame."""
        # Load the data
        df = analyzer.load_data()
        
        # Validate that we got a DataFrame
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        
        # Validate DataFrame has data
        assert len(df) > 0
        assert len(df.columns) > 0
        
        # Validate that the data was stored in the analyzer
        assert analyzer._dataframe is not None
        assert analyzer._dataframe.equals(df)
        
        # Test that we can get the DataFrame using get_dataframe method
        retrieved_df = analyzer.get_dataframe()
        assert retrieved_df.equals(df)
        
        # Clean up
        analyzer.close()
    
    def test_dataframe_structure_validation(self, analyzer):
        """Test that the DataFrame has the expected structure for leads data."""
        # Load the data
        df = analyzer.load_data()
        
        # Validate DataFrame shape: 52 rows of data (excluding header)
        assert df.shape == (52, 12), f"Expected (52, 12), got {df.shape}"
        
        # Validate first column is "Record ID"
        first_column = df.columns[0]
        assert first_column == "Record ID", f"Expected first column to be 'Record ID', got '{first_column}'"
        
        # Validate last column is "Type"
        last_column = df.columns[-1]
        assert last_column == "Type", f"Expected last column to be 'Type', got '{last_column}'"
        
        # Validate we have exactly 12 columns
        assert len(df.columns) == 12, f"Expected 12 columns, got {len(df.columns)}"
        
        # Validate column names
        expected_columns = [
            'Record ID', 'Deal Name', 'Deal Stage', 'Deal owner', 'Amount', 
            'Product or service', 'Product or Service', 'Sale Conviction', 
            'Engagement Type', 'Joined', '$', 'Type'
        ]
        assert list(df.columns) == expected_columns, f"Column mismatch. Expected: {expected_columns}, Got: {list(df.columns)}"
        
        # Clean up
        analyzer.close()
    
    def test_can_use_context_manager(self, leads_file_path):
        """Test that we can use the analyzer as a context manager."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            df = analyzer.load_data()
            assert df is not None
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
        
        # Verify the connection was closed
        assert not analyzer.spreadsheet_manager.is_open
    
    def test_raises_error_for_missing_file(self):
        """Test that appropriate error is raised for missing file."""
        analyzer = SalesLeadAnalyzer(Path("data/raw/nonexistent.xlsx"), sheet_name="Sheet1")
        
        with pytest.raises(FileNotFoundError):
            analyzer.load_data()
    
    def test_raises_error_for_missing_sheet(self, leads_file_path):
        """Test that appropriate error is raised for missing sheet."""
        analyzer = SalesLeadAnalyzer(leads_file_path, sheet_name="Nonexistent Sheet")
        
        with pytest.raises(RuntimeError) as exc_info:
            analyzer.load_data()
        
        assert "Sheet 'Nonexistent Sheet' not found" in str(exc_info.value)
        analyzer.close()
    
    def test_raises_error_when_getting_dataframe_before_loading(self, analyzer):
        """Test that appropriate error is raised when trying to get DataFrame before loading."""
        with pytest.raises(RuntimeError) as exc_info:
            analyzer.get_dataframe()
        
        assert "Data not loaded" in str(exc_info.value)
    
    def test_default_sheet_name_behavior(self, leads_file_path):
        """Test that the default sheet name is 'Sheet1' when not specified."""
        analyzer = SalesLeadAnalyzer(leads_file_path)  # No sheet_name parameter
        assert analyzer._sheet_name == "Sheet1"
        
        # This should fail because "Sheet1" doesn't exist in leads.xlsx
        with pytest.raises(RuntimeError) as exc_info:
            analyzer.load_data()
        
        assert "Sheet 'Sheet1' not found" in str(exc_info.value)
        analyzer.close() 