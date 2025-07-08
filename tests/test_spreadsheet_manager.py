# tests/test_spreadsheet_manager.py
import pytest
from pathlib import Path
from src.tool_experiments.spreadsheet_manager import SpreadsheetManager
import pandas as pd


class TestSpreadsheetManager:
    """Test cases for SpreadsheetManager class."""
    
    @pytest.fixture
    def test_file_path(self):
        """Path to test spreadsheet in data/raw directory."""
        return Path("data/raw/testTimeSheet.xlsx")  # Adjust filename as needed
    
    @pytest.fixture
    def manager(self, test_file_path):
        """Create a SpreadsheetManager instance for testing."""
        return SpreadsheetManager(test_file_path)
    
    # ============================================================================
    # PRIMARY TESTS - Core Functional Behavior
    # ============================================================================
    
    @pytest.mark.primary
    def test_can_read_range_as_dataframe(self, manager):
        """Primary test: Shows the main data loading capability with auto-detection."""
        manager.open()
        # Read entire range with no parameters (should auto-detect)
        df = manager.readRangeAsDataFrame()
        
        # Validate DataFrame structure
        assert df is not None
        assert len(df.columns) == 5  # 5 columns
        assert len(df) == 11  # 11 rows of data (excluding header)
        
        # Validate that first row contains headers
        expected_headers = ['Date', 'Start', 'Stop', 'Purpose', 'Time']
        assert list(df.columns) == expected_headers
    
    @pytest.mark.primary
    def test_can_write_and_read_dataframe(self):
        """Primary test: Shows the main data writing capability with round-trip validation."""
        from pathlib import Path
        import pandas as pd
        
        # Create a controlled test DataFrame
        test_data = {
            'Name': ['Alice', 'Bob'],
            'Age': [25, 30]
        }
        test_df = pd.DataFrame(test_data)
        
        # Create path for new spreadsheet in data/output folder
        output_path = Path("data/output/test_dataframe_write.xlsx")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create new spreadsheet and write DataFrame
        with SpreadsheetManager.CreateNew(output_path, "TestSheet") as manager:
            # Write DataFrame starting at cell B2 (not A1 to test positioning)
            manager.write_dataframe(test_df, "TestSheet", start_cell="B2", include_headers=True)
            
            # Verify the data was written correctly by reading specific cells
            assert manager.read_cell("TestSheet", "B2") == "Name"
            assert manager.read_cell("TestSheet", "C2") == "Age"
            assert manager.read_cell("TestSheet", "B3") == "Alice"
            assert manager.read_cell("TestSheet", "C3") == 25
            assert manager.read_cell("TestSheet", "B4") == "Bob"
            assert manager.read_cell("TestSheet", "C4") == 30
        
        # Now read the DataFrame back using the readRangeAsDataFrame method
        with SpreadsheetManager(output_path) as manager:
            # Read the range that contains our data (B2:C4)
            read_df = manager.readRangeAsDataFrame(
                sheet_name="TestSheet",
                start_row=2, end_row=4,
                start_col="B", end_col="C"
            )
            
            # Debug: print what we actually read
            print(f"Read DataFrame shape: {read_df.shape}")
            print(f"Read DataFrame:\n{read_df}")
            print(f"Read DataFrame columns: {list(read_df.columns)}")
            
            # Validate the DataFrame structure and content
            assert len(read_df) == 2  # 2 rows of data
            assert len(read_df.columns) == 2  # 2 columns
            assert list(read_df.columns) == ["Name", "Age"]
            assert read_df.iloc[0]["Name"] == "Alice"
            assert read_df.iloc[0]["Age"] == 25
            assert read_df.iloc[1]["Name"] == "Bob"
            assert read_df.iloc[1]["Age"] == 30
    
    @pytest.mark.primary
    def test_can_create_new_spreadsheet(self):
        """Primary test: Shows spreadsheet creation capability."""
        from pathlib import Path
        
        # Create path for new spreadsheet in data/output folder
        output_path = Path("data/output/test_new_spreadsheet.xlsx")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create new spreadsheet using class method
        with SpreadsheetManager.CreateNew(output_path, "TestSheet") as manager:
            # Verify the spreadsheet was created and opened
            assert manager.is_open is True
            assert manager.workbook is not None
            
            # Verify the sheet name
            sheet_names = manager.get_sheet_names()
            assert "TestSheet" in sheet_names
            assert len(sheet_names) == 1
        
        # Verify the file exists after closing
        assert output_path.exists()
        assert output_path.stat().st_size > 0  # File should not be empty
    
    # ============================================================================
    # COVERAGE TESTS - Resilience & Edge Cases
    # ============================================================================
    
    def test_can_create_manager(self, test_file_path):
        """Coverage test: Setup - basic instantiation."""
        manager = SpreadsheetManager(test_file_path)
        assert manager is not None
        assert manager.file_path == test_file_path
    
    def test_can_open_spreadsheet(self, manager):
        """Coverage test: Setup - basic operations."""
        manager.open()
        assert manager.workbook is not None
        assert manager.is_open is True
    
    def test_can_get_sheet_names(self, manager):
        """Coverage test: Setup - basic operations."""
        manager.open()
        sheet_names = manager.get_sheet_names()
        assert isinstance(sheet_names, list)
        assert len(sheet_names) > 0
    
    def test_can_read_cell_value(self, manager):
        """Coverage test: Edge case - specific cell reading."""
        manager.open()
        # Assuming A1 has some content - adjust based on your test file
        value = manager.read_cell("Sheet1", "D1")  # or whatever your sheet is called
        assert value == 'Purpose'
    
    def test_can_read_cell_coordinates(self, manager):
        """Coverage test: Edge case - coordinate-based reading."""
        manager.open()
        value = manager.read_cell_coords("Sheet1", row=1, col=1)  # A1
        assert value is not None
    
    def test_can_close_spreadsheet(self, manager):
        """Coverage test: Setup - resource management."""
        manager.open()
        assert manager.is_open is True
        manager.close()
        assert manager.is_open is False

    def test_can_find_next_empty_cell_in_column(self, manager):
        """Coverage test: Edge case - utility function."""
        manager.open()
        # Find next empty cell in column A starting from row 2
        empty_row = manager.find_next_empty_cell_in_column("Sheet1", "A", start_row=2)
        assert empty_row == 13


