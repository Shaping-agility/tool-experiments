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
    

    
    def test_can_create_analyzer(self, leads_file_path):
        """Test that we can create a SalesLeadAnalyzer instance."""
        analyzer = SalesLeadAnalyzer(leads_file_path, sheet_name="All deals")
        assert analyzer is not None
        assert analyzer.file_path == leads_file_path
        assert analyzer._sheet_name == "All deals"
    
    def test_can_load_leads_spreadsheet(self, leads_file_path):
        """Test that we can open leads.xlsx and load the 'All deals' sheet as DataFrame."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
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
    
    def test_dataframe_structure_validation(self, leads_file_path):
        """Test that the DataFrame has the expected structure for leads data."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            # Load the data
            df = analyzer.load_data()
            
            # Validate DataFrame shape: 52 rows of data (excluding header), 13 columns (including Sector)
            assert df.shape == (52, 13), f"Expected (52, 13), got {df.shape}"
            
            # Validate first column is "Record ID"
            first_column = df.columns[0]
            assert first_column == "Record ID", f"Expected first column to be 'Record ID', got '{first_column}'"
            
            # Validate last column is "Sector" (the calculated field)
            last_column = df.columns[-1]
            assert last_column == "Sector", f"Expected last column to be 'Sector', got '{last_column}'"
            
            # Validate we have exactly 13 columns
            assert len(df.columns) == 13, f"Expected 13 columns, got {len(df.columns)}"
            
            # Validate column names (including the new Sector column)
            expected_columns = [
                'Record ID', 'Deal Name', 'Deal Stage', 'Deal owner', 'Amount', 
                'Product or service', 'Product or Service', 'Sale Conviction', 
                'Engagement Type', 'Joined', '$', 'Type', 'Sector'
            ]
            assert list(df.columns) == expected_columns, f"Column mismatch. Expected: {expected_columns}, Got: {list(df.columns)}"
    
    def test_sector_field_calculation(self, leads_file_path):
        """Test that the Sector field is calculated correctly based on Deal owner."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            # Load the data
            df = analyzer.load_data()
            
            # Verify the Sector column exists
            assert 'Sector' in df.columns, "Sector column should be added to DataFrame"
            
            # Verify we now have 13 columns (original 12 + new Sector column)
            assert len(df.columns) == 13, f"Expected 13 columns after adding Sector, got {len(df.columns)}"
            
            # Test specific rows based on Deal owner
            # First row (index 0) - should be Government
            first_row_sector = df.iloc[0]['Sector']
            first_row_owner = df.iloc[0]['Deal owner']
            assert first_row_sector == "Government", f"First row should be Government, got {first_row_sector} (owner: {first_row_owner})"
            
            # Fifth row (index 4) - should be Industry
            fifth_row_sector = df.iloc[4]['Sector']
            fifth_row_owner = df.iloc[4]['Deal owner']
            assert fifth_row_sector == "Industry", f"Fifth row should be Industry, got {fifth_row_sector} (owner: {fifth_row_owner})"
            
            # Verify all industry owners are correctly classified
            industry_owners = ["Hamish Bignell", "Paul Tardio", "Beth Reeve", "Katie King"]
            for owner in industry_owners:
                owner_rows = df[df['Deal owner'] == owner]
                if len(owner_rows) > 0:  # Only test if this owner exists in the data
                    for _, row in owner_rows.iterrows():
                        assert row['Sector'] == "Industry", f"Owner {owner} should be classified as Industry"
            
            # Verify all other owners are classified as Government
            non_industry_rows = df[~df['Deal owner'].isin(industry_owners)]
            for _, row in non_industry_rows.iterrows():
                assert row['Sector'] == "Government", f"Owner {row['Deal owner']} should be classified as Government"
    
    def test_getSummaryLeads_method(self, leads_file_path):
        """Test the getSummaryLeads method with specific filtering criteria."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            # Load the data
            analyzer.load_data()
            
            # Test the specific example: Sector=Industry, Conviction=High, Type=Product
            result_df = analyzer.getSummaryLeads(sector="Industry", conviction="High", engagement_type="Product")
            
            # Verify we got a DataFrame
            assert isinstance(result_df, pd.DataFrame)
            
            # Verify we have exactly 2 rows as expected
            assert len(result_df) == 2, f"Expected 2 rows, got {len(result_df)}"
            
            # Verify we have exactly 3 columns: Deal Name, Deal owner, Amount
            expected_columns = ['Deal Name', 'Deal owner', 'Amount']
            assert list(result_df.columns) == expected_columns, f"Expected columns {expected_columns}, got {list(result_df.columns)}"
            
            # Verify the deal names start with expected values
            deal_names = result_df['Deal Name'].tolist()
            assert any(name.startswith("Westpac") for name in deal_names), "Expected a deal starting with 'Westpac'"
            assert any(name.startswith("Central") for name in deal_names), "Expected a deal starting with 'Central'"
            
            # Verify all rows have the correct sector, conviction, and engagement type
            full_df = analyzer.get_dataframe()
            for _, row in result_df.iterrows():
                # Find the corresponding row in the full DataFrame
                matching_rows = full_df[full_df['Deal Name'] == row['Deal Name']]
                assert len(matching_rows) == 1, f"Should find exactly one matching row for {row['Deal Name']}"
                
                matching_row = matching_rows.iloc[0]
                assert matching_row['Sector'] == "Industry", f"Expected Industry sector for {row['Deal Name']}"
                assert matching_row['Sale Conviction'] == "High", f"Expected High conviction for {row['Deal Name']}"
                assert matching_row['Engagement Type'] == "Product", f"Expected Product engagement type for {row['Deal Name']}"
    
    def test_getSummaryLeads_with_no_matches(self, leads_file_path):
        """Test getSummaryLeads when no rows match the criteria."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            # Load the data
            analyzer.load_data()
            
            # Test with criteria that should return no results
            result_df = analyzer.getSummaryLeads(sector="Industry", conviction="Low", engagement_type="Nonexistent")
            
            # Verify we got an empty DataFrame
            assert isinstance(result_df, pd.DataFrame)
            assert len(result_df) == 0
            assert list(result_df.columns) == ['Deal Name', 'Deal owner', 'Amount']
    
    def test_getSummaryLeads_without_loading_data(self, leads_file_path):
        """Test that getSummaryLeads raises an error when data hasn't been loaded."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            with pytest.raises(RuntimeError) as exc_info:
                analyzer.getSummaryLeads(sector="Industry", conviction="High", engagement_type="Product")
            
            assert "Data not loaded" in str(exc_info.value)
    
    def test_getSummaryTotal_method(self, leads_file_path):
        """Test the getSummaryTotal method with specific filtering criteria."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            analyzer.load_data()
            
            # Test the specific example: Sector=Industry, Conviction=High, Type=Product
            total = analyzer.getSummaryTotal(sector="Industry", conviction="High", engagement_type="Product")
            
            # Verify we got the expected total
            assert total == 270000, f"Expected total 270000, got {total}"
            
            # Test with no matches
            zero_total = analyzer.getSummaryTotal(sector="Industry", conviction="Low", engagement_type="Nonexistent")
            assert zero_total == 0, f"Expected total 0 for no matches, got {zero_total}"
    
    def test_getSummaryTotal_without_loading_data(self, leads_file_path):
        """Test that getSummaryTotal raises an error when data hasn't been loaded."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            with pytest.raises(RuntimeError) as exc_info:
                analyzer.getSummaryTotal(sector="Industry", conviction="High", engagement_type="Product")
            
            assert "Data not loaded" in str(exc_info.value)
    
    def test_getSummaryText_method(self, leads_file_path):
        """Test the getSummaryText method with specific filtering criteria."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            analyzer.load_data()
            
            # Test the specific example: Sector=Industry, Conviction=High, Type=Product
            summary_texts = analyzer.getSummaryText(sector="Industry", conviction="High", engagement_type="Product")
            
            # Verify we got a list of strings
            assert isinstance(summary_texts, list)
            assert len(summary_texts) == 2, f"Expected 2 summary texts, got {len(summary_texts)}"
            
            # Verify all items are strings
            for text in summary_texts:
                assert isinstance(text, str)
            
            # Verify the expected format and content
            expected_texts = [
                "Central Highlands Water - Placemaker Subscription - $70K",
                "Westpac - Renewal - $200K"
            ]
            
            # Sort both lists for comparison (order might vary)
            assert sorted(summary_texts) == sorted(expected_texts), f"Expected {expected_texts}, got {summary_texts}"
            
            # Test with no matches
            empty_texts = analyzer.getSummaryText(sector="Industry", conviction="Low", engagement_type="Nonexistent")
            assert empty_texts == [], f"Expected empty list for no matches, got {empty_texts}"
    
    def test_getSummaryText_amount_formatting(self, leads_file_path):
        """Test that getSummaryText correctly formats different amounts."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            analyzer.load_data()
            
            # Test various amount formatting scenarios
            # We'll test with a specific filter that gives us known amounts
            summary_texts = analyzer.getSummaryText(sector="Industry", conviction="High", engagement_type="Product")
            
            # Verify the amounts are formatted correctly
            for text in summary_texts:
                # Check that the format is "Deal Name - $XK"
                assert " - $" in text, f"Expected format 'Deal Name - $XK', got {text}"
                assert text.endswith("K"), f"Expected format to end with 'K', got {text}"
                
                # Extract the amount part and verify it's a number
                amount_part = text.split(" - $")[1].replace("K", "")
                amount_num = int(amount_part)
                assert amount_num > 0, f"Expected positive amount, got {amount_num}"
    
    def test_getSummaryText_without_loading_data(self, leads_file_path):
        """Test that getSummaryText raises an error when data hasn't been loaded."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
            with pytest.raises(RuntimeError) as exc_info:
                analyzer.getSummaryText(sector="Industry", conviction="High", engagement_type="Product")
            
            assert "Data not loaded" in str(exc_info.value)
    
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
    
    def test_raises_error_when_getting_dataframe_before_loading(self, leads_file_path):
        """Test that appropriate error is raised when trying to get DataFrame before loading."""
        with SalesLeadAnalyzer(leads_file_path, sheet_name="All deals") as analyzer:
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