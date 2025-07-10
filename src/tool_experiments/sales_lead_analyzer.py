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
        self.spreadsheet_manager.open()
        self._validate_sheet_exists()
        self._dataframe = self._read_sheet_as_dataframe()
        self._add_sector_field()
        return self._dataframe
    
    def _validate_sheet_exists(self):
        """Validate that the specified sheet exists in the workbook."""
        sheet_names = self.spreadsheet_manager.get_sheet_names()
        if self._sheet_name not in sheet_names:
            raise RuntimeError(f"Sheet '{self._sheet_name}' not found. Available sheets: {sheet_names}")
    
    def _read_sheet_as_dataframe(self) -> pd.DataFrame:
        """Read the specified sheet as a DataFrame."""
        return self.spreadsheet_manager.readRangeAsDataFrame(sheet_name=self._sheet_name)
    
    def _add_sector_field(self):
        """Add a calculated Sector field based on Deal owner and engagement type."""
        if self._dataframe is None:
            return
        
        industry_owners = self._get_industry_owners()
        
        def determine_sector(row):
            """Determine sector based on deal owner and engagement type."""
            owner = row['Deal owner']
            engagement_type = row['Engagement Type']
            
            # Handle "Consulting Government" as Government
            if engagement_type == "Consulting Government":
                return "Government"
            
            # Use deal owner logic for other cases
            return "Industry" if owner in industry_owners else "Government"
        
        self._dataframe['Sector'] = self._dataframe.apply(determine_sector, axis=1)
    
    def _get_industry_owners(self) -> list[str]:
        """Get the list of deal owners classified as Industry."""
        return ["Hamish Bignell", "Paul Tardio", "Beth Reeve", "Katie King"]
    
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
        self._ensure_data_loaded()
        filtered_df = self._filter_dataframe_by_criteria(sector, conviction, engagement_type)
        return self._select_summary_columns(filtered_df)
    
    def _ensure_data_loaded(self):
        """Ensure that data has been loaded before performing operations."""
        if self._dataframe is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
    
    def _filter_dataframe_by_criteria(self, sector: str, conviction: str, engagement_type: str) -> pd.DataFrame:
        """Filter the DataFrame based on sector, conviction, and engagement type criteria."""
        if self._dataframe is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        filtered = self._dataframe[
            (self._dataframe['Sector'] == sector) &
            (self._dataframe['Sale Conviction'] == conviction) &
            (self._dataframe['Engagement Type'] == engagement_type)
        ]
        if not isinstance(filtered, pd.DataFrame):
            filtered = filtered.to_frame().T if hasattr(filtered, 'to_frame') else pd.DataFrame([filtered])
        return filtered
    
    def _select_summary_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select only the Deal Name, Deal owner, and Amount columns from the DataFrame."""
        selected = df[['Deal Name', 'Deal owner', 'Amount']]
        if not isinstance(selected, pd.DataFrame):
            selected = selected.to_frame().T if hasattr(selected, 'to_frame') else pd.DataFrame([selected])
        return selected.copy()
    
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
        self._ensure_data_loaded()
        filtered_df = self.getSummaryLeads(sector, conviction, engagement_type)
        return self._calculate_total_amount(filtered_df)
    
    def _calculate_total_amount(self, df: pd.DataFrame) -> float:
        """Calculate the total sum of the Amount column."""
        return float(df['Amount'].sum())
    
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
        self._ensure_data_loaded()
        filtered_df = self.getSummaryLeads(sector, conviction, engagement_type)
        return self._convert_to_summary_texts(filtered_df)
    
    def _convert_to_summary_texts(self, df: pd.DataFrame) -> list[str]:
        """Convert DataFrame rows to summary text strings in the format 'Deal name - $amountK'."""
        summary_texts = []
        for _, row in df.iterrows():
            deal_name = str(row['Deal Name'])
            amount = float(row['Amount'])
            formatted_amount = self._format_amount_as_k(amount)
            summary_text = f"{deal_name} - {formatted_amount}"
            summary_texts.append(summary_text)
        return summary_texts
    
    def _format_amount_as_k(self, amount: float) -> str:
        """Format amount as currency in K format (e.g., $270K)."""
        amount_k = round(amount / 1000)
        return f"${amount_k}K"
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the loaded DataFrame.
        
        Returns:
            pandas DataFrame containing the leads data
            
        Raises:
            RuntimeError: If data hasn't been loaded yet
        """
        self._ensure_data_loaded()
        if self._dataframe is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        return self._dataframe
    
    def close(self):
        """Close the spreadsheet connection."""
        if self.spreadsheet_manager.is_open:
            self.spreadsheet_manager.close()
        self._clear_dataframe()
    
    def _clear_dataframe(self):
        """Clear the loaded DataFrame."""
        if self._dataframe is not None:
            self._dataframe = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 

    def getSummaryMarkdown(self) -> str:
        """Generate markdown summary for all sectors, convictions, and engagement types.
        
        Returns:
            Markdown formatted string with comprehensive leads summary
            
        Raises:
            RuntimeError: If data hasn't been loaded yet
        """
        self._ensure_data_loaded()
        
        sectors = ["Industry", "Government"]
        convictions = ["High", "Medium"]
        engagement_types = ["Product", "Consulting", "Product & Consulting"]
        
        markdown_lines = ["# Sales Lead Summary\n"]
        
        for sector in sectors:
            # markdown_lines.append(f"## {sector}\n")
            
            for conviction in convictions:
                #markdown_lines.append(f"### {conviction} Conviction\n")
                
                for engagement_type in engagement_types:
                    try:
                        leads_df = self.getSummaryLeads(sector, conviction, engagement_type)
                        total = self.getSummaryTotal(sector, conviction, engagement_type)
                        
                        if len(leads_df) > 0:
                            markdown_lines.append(f"## {sector} {conviction} conviction {engagement_type} - ${total:,.0f}\n")
                            # markdown_lines.append(f"#### {engagement_type}\n")
                            # markdown_lines.append(f"**Total:** ${total:,.0f}\n")
                            # markdown_lines.append("**Leads:**\n")
                            
                            # Get summary texts and add them as bullet points
                            summary_texts = self.getSummaryText(sector, conviction, engagement_type)
                            for text in summary_texts:
                                markdown_lines.append(f"- {text}")
                            
                            #deal_name = str(row['Deal Name'])
                            #amount = float(row['Amount'])
                            #formatted_amount = self._format_amount_as_k(amount)
                            #markdown_lines.append(f"- {deal_name} - {formatted_amount}")
                            
                            markdown_lines.append("")
                        # else:
                        #     # Include empty sections for completeness
                        #     #markdown_lines.append(f"#### {engagement_type}\n")
                        #     #markdown_lines.append("**Total:** $0\n")
                        #     #markdown_lines.append("**Leads:** None\n\n")
                        pass
                            
                    except Exception as e:
                        # Handle any errors gracefully
                        markdown_lines.append(f"#### {engagement_type}\n")
                        markdown_lines.append(f"**Error:** {str(e)}\n\n")
        
        return "\n".join(markdown_lines) 