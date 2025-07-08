# tests/test_sales_lead_analyzer.py
import pytest
from pathlib import Path
from src.tool_experiments.sales_lead_analyzer import SalesLeadAnalyzer
import pandas as pd


class TestSalesLeadAnalyzer:
    """Test cases for SalesLeadAnalyzer class."""
    
    @classmethod
    def setup_class(cls):
        """Class-level setup: create analyzer instance."""
        leads_file_path = Path("data/raw/Leads.xlsx")
        cls.analyzer = SalesLeadAnalyzer(leads_file_path, sheet_name="All deals")

    @classmethod
    def teardown_class(cls):
        """Class-level teardown: close analyzer instance."""
        cls.analyzer.close()
        cls.analyzer._dataframe = None  # Ensure cleanup
    
    # ============================================================================
    # PRIMARY TESTS - Core Functional Behavior
    # ============================================================================
    
    @pytest.mark.primary
    def test_can_load_leads_spreadsheet(self):
        """Primary test: Shows how to load leads data from spreadsheet."""
        df = self.analyzer.load_data()
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert len(df.columns) > 0
        assert self.analyzer._dataframe is not None
        assert self.analyzer._dataframe.equals(df)
        retrieved_df = self.analyzer.get_dataframe()
        assert retrieved_df.equals(df)
    
    @pytest.mark.primary
    def test_sector_field_calculation(self):
        """Primary test: Demonstrates the key business logic - Sector calculation based on Deal owner."""
        df = self.analyzer.load_data()
        assert 'Sector' in df.columns, "Sector column should be added to DataFrame"
        assert len(df.columns) == 13, f"Expected 13 columns after adding Sector, got {len(df.columns)}"
        first_row_sector = df.iloc[0]['Sector']
        first_row_owner = df.iloc[0]['Deal owner']
        assert first_row_sector == "Government", f"First row should be Government, got {first_row_sector} (owner: {first_row_owner})"
        fifth_row_sector = df.iloc[4]['Sector']
        fifth_row_owner = df.iloc[4]['Deal owner']
        assert fifth_row_sector == "Industry", f"Fifth row should be Industry, got {fifth_row_sector} (owner: {fifth_row_owner})"
        industry_owners = ["Hamish Bignell", "Paul Tardio", "Beth Reeve", "Katie King"]
        for owner in industry_owners:
            owner_rows = df[df['Deal owner'] == owner]
            if len(owner_rows) > 0:
                for _, row in owner_rows.iterrows():
                    assert row['Sector'] == "Industry", f"Owner {owner} should be classified as Industry"
        non_industry_rows = df[~df['Deal owner'].isin(industry_owners)]
        for _, row in non_industry_rows.iterrows():
            assert row['Sector'] == "Government", f"Owner {row['Deal owner']} should be classified as Government"
    
    @pytest.mark.primary
    def test_getSummaryLeads_method(self):
        """Primary test: Shows the main filtering capability with specific criteria."""
        self.analyzer.load_data()
        result_df = self.analyzer.getSummaryLeads(sector="Industry", conviction="High", engagement_type="Product")
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 2, f"Expected 2 rows, got {len(result_df)}"
        expected_columns = ['Deal Name', 'Deal owner', 'Amount']
        assert list(result_df.columns) == expected_columns, f"Expected columns {expected_columns}, got {list(result_df.columns)}"
        deal_names = result_df['Deal Name'].tolist()
        assert any(name.startswith("Westpac") for name in deal_names), "Expected a deal starting with 'Westpac'"
        assert any(name.startswith("Central") for name in deal_names), "Expected a deal starting with 'Central'"
        full_df = self.analyzer.get_dataframe()
        for _, row in result_df.iterrows():
            matching_rows = full_df[full_df['Deal Name'] == row['Deal Name']]
            assert len(matching_rows) == 1, f"Should find exactly one matching row for {row['Deal Name']}"
            matching_row = matching_rows.iloc[0]
            assert matching_row['Sector'] == "Industry", f"Expected Industry sector for {row['Deal Name']}"
            assert matching_row['Sale Conviction'] == "High", f"Expected High conviction for {row['Deal Name']}"
            assert matching_row['Engagement Type'] == "Product", f"Expected Product engagement type for {row['Deal Name']}"
    
    @pytest.mark.primary
    def test_getSummaryTotal_method(self):
        """Primary test: Shows the main aggregation capability with specific criteria."""
        self.analyzer.load_data()
        total = self.analyzer.getSummaryTotal(sector="Industry", conviction="High", engagement_type="Product")
        assert total == 270000, f"Expected total 270000, got {total}"
        zero_total = self.analyzer.getSummaryTotal(sector="Industry", conviction="Low", engagement_type="Nonexistent")
        assert zero_total == 0, f"Expected total 0 for no matches, got {zero_total}"
    
    @pytest.mark.primary
    def test_getSummaryText_method(self):
        """Primary test: Shows the main reporting capability with formatted text output."""
        self.analyzer.load_data()
        summary_texts = self.analyzer.getSummaryText(sector="Industry", conviction="High", engagement_type="Product")
        assert isinstance(summary_texts, list)
        assert len(summary_texts) == 2, f"Expected 2 summary texts, got {len(summary_texts)}"
        for summary_text in summary_texts:
            assert isinstance(summary_text, str)
            assert len(summary_text) > 0
        all_text = " ".join(summary_texts)
        assert "Westpac" in all_text, "Expected 'Westpac' in summary text"
        assert "Central" in all_text, "Expected 'Central' in summary text"
    
    # ============================================================================
    # COVERAGE TESTS - Resilience & Edge Cases
    # ============================================================================
    
    def test_can_create_analyzer(self):
        """Coverage test: Setup - basic instantiation."""
        assert self.analyzer is not None
        assert self.analyzer.file_path == Path("data/raw/Leads.xlsx")
        assert self.analyzer._sheet_name == "All deals"
    
    def test_dataframe_structure_validation(self):
        """Coverage test: Validation - data structure integrity."""
        df = self.analyzer.load_data()
        assert df.shape == (52, 13), f"Expected (52, 13), got {df.shape}"
        first_column = df.columns[0]
        assert first_column == "Record ID", f"Expected first column to be 'Record ID', got '{first_column}'"
        last_column = df.columns[-1]
        assert last_column == "Sector", f"Expected last column to be 'Sector', got '{last_column}'"
        assert len(df.columns) == 13, f"Expected 13 columns, got {len(df.columns)}"
        expected_columns = [
            'Record ID', 'Deal Name', 'Deal Stage', 'Deal owner', 'Amount', 
            'Product or service', 'Product or Service', 'Sale Conviction', 
            'Engagement Type', 'Joined', '$', 'Type', 'Sector'
        ]
        assert list(df.columns) == expected_columns, f"Column mismatch. Expected: {expected_columns}, Got: {list(df.columns)}"
    
    def test_getSummaryLeads_with_no_matches(self):
        """Coverage test: Edge case - empty results."""
        self.analyzer.load_data()
        result_df = self.analyzer.getSummaryLeads(sector="Industry", conviction="Low", engagement_type="Nonexistent")
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 0
        assert list(result_df.columns) == ['Deal Name', 'Deal owner', 'Amount']
    
    def test_getSummaryLeads_without_loading_data(self):
        """Coverage test: Error handling - state management."""
        analyzer = SalesLeadAnalyzer(Path("data/raw/Leads.xlsx"), sheet_name="All deals")
        with pytest.raises(RuntimeError) as exc_info:
            analyzer.getSummaryLeads(sector="Industry", conviction="High", engagement_type="Product")
        assert "Data not loaded" in str(exc_info.value)
        analyzer.close()
    
    def test_getSummaryTotal_without_loading_data(self):
        """Coverage test: Error handling - state management."""
        analyzer = SalesLeadAnalyzer(Path("data/raw/Leads.xlsx"), sheet_name="All deals")
        with pytest.raises(RuntimeError) as exc_info:
            analyzer.getSummaryTotal(sector="Industry", conviction="High", engagement_type="Product")
        assert "Data not loaded" in str(exc_info.value)
        analyzer.close()
    
    def test_getSummaryText_amount_formatting(self):
        """Coverage test: Edge case - formatting behavior."""
        self.analyzer.load_data()
        summary_texts = self.analyzer.getSummaryText(sector="Industry", conviction="High", engagement_type="Product")
        for summary_text in summary_texts:
            if "270000" in summary_text:
                assert "270,000" in summary_text or "270000" in summary_text, "Amount should be properly formatted"
    
    def test_getSummaryText_without_loading_data(self):
        """Coverage test: Error handling - state management."""
        with SalesLeadAnalyzer(Path("data/raw/Leads.xlsx"), sheet_name="All deals") as analyzer:
            with pytest.raises(RuntimeError) as exc_info:
                analyzer.getSummaryText(sector="Industry", conviction="High", engagement_type="Product")
        assert "Data not loaded" in str(exc_info.value)
    
    def test_can_use_context_manager(self):
        """Coverage test: Integration - context manager usage."""
        with SalesLeadAnalyzer(Path("data/raw/Leads.xlsx"), sheet_name="All deals") as analyzer:
            df = analyzer.load_data()
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
        assert not hasattr(analyzer, '_dataframe') or analyzer._dataframe is None
    
    def test_raises_error_for_missing_file(self):
        """Coverage test: Error handling - file system issues."""
        with pytest.raises(FileNotFoundError):
            SalesLeadAnalyzer(Path("data/raw/nonexistent.xlsx"), sheet_name="All deals").load_data()
    
    def test_raises_error_for_missing_sheet(self):
        """Coverage test: Error handling - resource issues."""
        with pytest.raises(RuntimeError) as exc_info:
            with SalesLeadAnalyzer(Path("data/raw/Leads.xlsx"), sheet_name="NonexistentSheet") as analyzer:
                analyzer.load_data()
        assert "Sheet 'NonexistentSheet' not found" in str(exc_info.value)
    
    def test_raises_error_when_getting_dataframe_before_loading(self):
        """Coverage test: Error handling - state management."""
        analyzer = SalesLeadAnalyzer(Path("data/raw/Leads.xlsx"), sheet_name="All deals")
        with pytest.raises(RuntimeError) as exc_info:
            analyzer.get_dataframe()
        assert "Data not loaded" in str(exc_info.value)
        analyzer.close()
    
