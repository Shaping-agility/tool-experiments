from pathlib import Path
from openpyxl import load_workbook
from typing import Optional, List, Any
import pandas as pd

class SpreadsheetManager:
    """Manages reading and writing operations for Excel spreadsheets."""

    @classmethod
    def CreateNew(cls, file_path: Path, sheet_name: str = "Sheet1"):
        """Create a new Excel spreadsheet file.
        
        Args:
            file_path: Path where the new spreadsheet should be created
            sheet_name: Name of the first sheet (default: "Sheet1")
            
        Returns:
            SpreadsheetManager instance with the new workbook
        """
        from openpyxl import Workbook
        
        # Create a new workbook
        workbook = Workbook()
        
        # Remove the default sheet and create one with the specified name
        if workbook.active:
            workbook.remove(workbook.active)
        workbook.create_sheet(title=sheet_name)
        
        # Save the workbook
        workbook.save(file_path)
        workbook.close()
        
        # Create and return a SpreadsheetManager instance
        manager = cls(file_path)
        manager.workbook = load_workbook(file_path)
        manager.is_open = True
        return manager

    def __init__(self, file_path: Path):
        """Initialize with path to spreadsheet file."""
        self.file_path = Path(file_path)
        self.workbook = None
        self.is_open = False

    def open(self):
        """Open the spreadsheet file."""
        if not self.file_path.exists():raise FileNotFoundError(f"Spreadsheet not found: {self.file_path}")

        self.workbook = load_workbook(self.file_path)
        self.is_open = True

    def close(self) -> None:
        """Close the spreadsheet."""
        if self.workbook:
            self.workbook.close()
        self.workbook = None
        self.is_open = False
    
    def get_sheet_names(self) -> List[str]:
        """Get list of all sheet names in the workbook."""
        if not self.is_open:
            raise RuntimeError("Spreadsheet must be opened first")
        return self.workbook.sheetnames
    
    def read_cell(self, sheet_name: str, cell_address: str) -> Any:
        """Read value from a specific cell using A1 notation."""
        if not self.is_open:
            raise RuntimeError("Spreadsheet must be opened first")
        
        sheet = self.workbook[sheet_name]
        return sheet[cell_address].value
    
    def read_cell_coords(self, sheet_name: str, row: int, col: int) -> Any:
        """Read value from a specific cell using row/column coordinates."""
        if not self.is_open:
            raise RuntimeError("Spreadsheet must be opened first")
        
        sheet = self.workbook[sheet_name]
        return sheet.cell(row=row, column=col).value
    
    def find_next_empty_cell_in_column(self, sheet_name: str, column: str, start_row: int = 1) -> int:
        """Find the next empty cell in a column starting from start_row.
        
        Args:
            sheet_name: Name of the sheet to search
            column: Column letter (e.g., 'A', 'B', etc.)
            start_row: Row number to start searching from (default: 1)
            
        Returns:
            Row number of the next empty cell
        """
        if not self.is_open:
            raise RuntimeError("Spreadsheet must be opened first")
        
        sheet = self.workbook[sheet_name]
        col_letter = column.upper()
        
        # Find the maximum row that has data in the sheet
        max_row = sheet.max_row
        
        # Search from start_row to max_row
        for row in range(start_row, max_row + 1):
            cell_value = sheet[f"{col_letter}{row}"].value
            if cell_value is None or str(cell_value).strip() == "":
                return row
        
        # If no empty cell found, return the next row after max_row
        return max_row + 1
    
    def readRangeAsDataFrame(self, sheet_name: Optional[str] = None, 
                           start_row: Optional[int] = None, end_row: Optional[int] = None,
                           start_col: Optional[str] = None, end_col: Optional[str] = None) -> pd.DataFrame:
        """Read a range of cells as a pandas DataFrame.
        
        Args:
            sheet_name: Name of the sheet to read (default: first sheet)
            start_row: Starting row number (default: 1)
            end_row: Ending row number (default: auto-detect)
            start_col: Starting column letter (default: 'A')
            end_col: Ending column letter (default: auto-detect)
            
        Returns:
            pandas DataFrame containing the range data
        """
        if not self.is_open:
            raise RuntimeError("Spreadsheet must be opened first")
        
        # Use first sheet if not specified
        if sheet_name is None:
            if self.workbook is None:
                raise RuntimeError("Workbook is not open")
            sheet_name = self.workbook.sheetnames[0]
        
        sheet = self.workbook[sheet_name]
        
        # Set defaults
        start_row = start_row or 1
        start_col = start_col or 'A'
        
        # Auto-detect end column if not specified
        if end_col is None:
            end_col = self._find_last_non_empty_column(sheet, start_row)
        
        # Auto-detect end row if not specified
        if end_row is None:
            end_row = self._find_last_non_empty_row(sheet, start_col)
        
        # Convert column letters to column indices
        start_col_idx = self._column_letter_to_index(start_col)
        end_col_idx = self._column_letter_to_index(end_col)
        
        # Read the range
        data = []
        for row in range(start_row, end_row + 1):
            row_data = []
            for col in range(start_col_idx, end_col_idx + 1):
                cell_value = sheet.cell(row=row, column=col).value
                row_data.append(cell_value)
            data.append(row_data)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Set column headers if we have data
        if len(data) > 0:
            # Use first row as headers if it's not empty
            if any(cell is not None and str(cell).strip() != "" for cell in data[0]):
                df.columns = df.iloc[0]
                df = df.iloc[1:].reset_index(drop=True)
        
        return df
    
    def write_dataframe(self, df: pd.DataFrame, sheet_name: str, start_cell: str = "A1", 
                       include_headers: bool = True) -> None:
        """Write a pandas DataFrame to a specified sheet and location.
        
        Args:
            df: DataFrame to write
            sheet_name: Name of the sheet to write to
            start_cell: Starting cell address (e.g., "A1", "B3")
            include_headers: Whether to include DataFrame column headers (default: True)
        """
        if not self.is_open:
            raise RuntimeError("Spreadsheet must be opened first")
        
        sheet = self.workbook[sheet_name]
        
        # Parse start cell to get row and column
        start_row, start_col = self._parse_cell_address(start_cell)
        
        # Write headers if requested
        if include_headers:
            for col_idx, header in enumerate(df.columns):
                cell_address = self._get_cell_address(start_row, start_col + col_idx)
                sheet[cell_address] = header
            data_start_row = start_row + 1
        else:
            data_start_row = start_row
        
        # Write data
        for row_idx, row_data in enumerate(df.values):
            for col_idx, value in enumerate(row_data):
                cell_address = self._get_cell_address(data_start_row + row_idx, start_col + col_idx)
                sheet[cell_address] = value
        
        # Save the workbook to persist changes
        if self.workbook:
            self.workbook.save(self.file_path)
    
    def _parse_cell_address(self, cell_address: str) -> tuple[int, int]:
        """Parse cell address (e.g., 'A1') to row and column indices."""
        import re
        
        # Match pattern like 'A1', 'B2', 'AA10', etc.
        match = re.match(r'^([A-Z]+)(\d+)$', cell_address.upper())
        if not match:
            raise ValueError(f"Invalid cell address: {cell_address}")
        
        col_letter = match.group(1)
        row_num = int(match.group(2))
        
        col_idx = self._column_letter_to_index(col_letter)
        return row_num, col_idx
    
    def _get_cell_address(self, row: int, col: int) -> str:
        """Convert row and column indices to cell address."""
        col_letter = self._column_index_to_letter(col)
        return f"{col_letter}{row}"
    
    def _find_last_non_empty_column(self, sheet, row: int) -> str:
        """Find the last non-empty column in a given row."""
        max_col = sheet.max_column
        for col in range(max_col, 0, -1):
            cell_value = sheet.cell(row=row, column=col).value
            if cell_value is not None and str(cell_value).strip() != "":
                return self._column_index_to_letter(col)
        return 'A'  # Default to A if no data found
    
    def _find_last_non_empty_row(self, sheet, column: str) -> int:
        """Find the last non-empty row in a given column."""
        max_row = sheet.max_row
        col_idx = self._column_letter_to_index(column)
        
        for row in range(max_row, 0, -1):
            cell_value = sheet.cell(row=row, column=col_idx).value
            if cell_value is not None and str(cell_value).strip() != "":
                return row
        return 1  # Default to 1 if no data found
    
    def _column_letter_to_index(self, column: str) -> int:
        """Convert column letter to index (A=1, B=2, etc.)."""
        result = 0
        for char in column.upper():
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result
    
    def _column_index_to_letter(self, index: int) -> str:
        """Convert column index to letter (1=A, 2=B, etc.)."""
        result = ""
        while index > 0:
            index -= 1
            result = chr(ord('A') + (index % 26)) + result
            index //= 26
        return result
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()