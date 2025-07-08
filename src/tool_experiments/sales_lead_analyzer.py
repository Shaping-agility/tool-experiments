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
        
        # Add calculated Sector field based on Deal owner
        self._add_sector_field()
        
        return self._dataframe
    
    def _add_sector_field(self):
        """Add a calculated Sector field based on Deal owner."""
        if self._dataframe is None:
            return
        
        # Define industry deal owners
        industry_owners = ["Hamish Bignell", "Paul Tardio", "Beth Reeve", "Katie King"]
        
        # Create the Sector column based on Deal owner
        self._dataframe['Sector'] = self._dataframe['Deal owner'].apply(
            lambda owner: "Industry" if owner in industry_owners else "Government"
        )
    
    def getSummaryLeads(self, sector: str, conviction: str, engagement_type: str) -> pd.DataFrame:
        """Get a filtered summary of leads based on sector, conviction, and engagement type.
        
        Args:
            sector: The sector to filter by ("Industry" or "Government")
            conviction: The sale conviction level to filter by
            engagement_type: The engagement type to filter by
            
        Returns:
            pandas DataFrame with filtered rows containing only Deal Name, Deal Owner, and Amount columns
            
        Raises:
            RuntimeError: If data hasn't been loaded yet
        """
        if self._dataframe is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        # Filter the DataFrame based on the specified criteria
        filtered_df = self._dataframe[
            (self._dataframe['Sector'] == sector) &
            (self._dataframe['Sale Conviction'] == conviction) &
            (self._dataframe['Engagement Type'] == engagement_type)
        ]
        
        # Select only the specified columns
        result_df = filtered_df[['Deal Name', 'Deal owner', 'Amount']].copy()
        
        return result_df
    
    def getSummaryTotal(self, sector: str, conviction: str, engagement_type: str) -> float:
        """Get the total value of leads based on sector, conviction, and engagement type.
        
        Args:
            sector: The sector to filter by ("Industry" or "Government")
            conviction: The sale conviction level to filter by
            engagement_type: The engagement type to filter by
            
        Returns:
            Total sum of the Amount column for matching leads
            
        Raises:
            RuntimeError: If data hasn't been loaded yet
        """
        if self._dataframe is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        # Get the filtered DataFrame using getSummaryLeads
        filtered_df = self.getSummaryLeads(sector, conviction, engagement_type)
        
        # Sum the Amount column
        total = filtered_df['Amount'].sum()
        
        return total
    
    def getSummaryText(self, sector: str, conviction: str, engagement_type: str) -> list[str]:
        """Get a text summary of leads based on sector, conviction, and engagement type.
        
        Args:
            sector: The sector to filter by ("Industry" or "Government")
            conviction: The sale conviction level to filter by
            engagement_type: The engagement type to filter by
            
        Returns:
            List of strings in format "<Deal name> - $<amount>K" where amount is rounded to nearest K
            
        Raises:
            RuntimeError: If data hasn't been loaded yet
        """
        if self._dataframe is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        # Get the filtered DataFrame using getSummaryLeads
        filtered_df = self.getSummaryLeads(sector, conviction, engagement_type)
        
        # Convert each row to the required string format
        summary_texts = []
        for _, row in filtered_df.iterrows():
            deal_name = row['Deal Name']
            amount = row['Amount']
            
            # Convert amount to K format with rounding
            amount_k = round(amount / 1000)
            formatted_amount = f"${amount_k}K"
            
            # Create the summary string
            summary_text = f"{deal_name} - {formatted_amount}"
            summary_texts.append(summary_text)
        
        return summary_texts
    
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