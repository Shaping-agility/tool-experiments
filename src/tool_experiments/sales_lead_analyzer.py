from pathlib import Path
from typing import Optional
import pandas as pd
from .spreadsheet_manager import SpreadsheetManager


class SalesLeadAnalyzer:
    """Analyzes sales lead data from Excel spreadsheets."""
    
    def __init__(self, file_path: Optional[Path] = None, sheet_name: str = "Sheet1"):
        """Initialize the SalesLeadAnalyzer.
        
        Args:
            file_path: Path to the leads spreadsheet. Defaults to data/raw/Leads.xlsx
            sheet_name: Name of the sheet to analyze. Defaults to "Sheet1"
        """
        if file_path is None:
            self.file_path = Path("data/raw/Leads.xlsx")
        else:
            self.file_path = Path(file_path)
        
        self.spreadsheet_manager = SpreadsheetManager(self.file_path)
        self._dataframe: Optional[pd.DataFrame] = None
        self._sheet_name = sheet_name
    
    def load_data(self) -> pd.DataFrame:
        """Load the specified sheet as a DataFrame.
        
        Returns:
            pandas DataFrame containing the leads data
            
        Raises:
            FileNotFoundError: If the spreadsheet file doesn't exist
            RuntimeError: If the specified sheet doesn't exist
        """
        # Open the spreadsheet
        self.spreadsheet_manager.open()
        
        # Verify the 'All deals' sheet exists
        sheet_names = self.spreadsheet_manager.get_sheet_names()
        if self._sheet_name not in sheet_names:
            raise RuntimeError(f"Sheet '{self._sheet_name}' not found. Available sheets: {sheet_names}")
        
        # Load the data as DataFrame
        self._dataframe = self.spreadsheet_manager.readRangeAsDataFrame(sheet_name=self._sheet_name)
        
        return self._dataframe
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the loaded DataFrame.
        
        Returns:
            pandas DataFrame containing the leads data
            
        Raises:
            RuntimeError: If data hasn't been loaded yet
        """
        if self._dataframe is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        return self._dataframe
    
    def close(self):
        """Close the spreadsheet connection."""
        if self.spreadsheet_manager.is_open:
            self.spreadsheet_manager.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 