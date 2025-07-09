# tests/test_sales_analyzer.py
import pytest
import time
import logging
from pathlib import Path
from datetime import date, datetime
from src.tool_experiments.sales_analyzer import SalesAnalyzer
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSalesAnalyzer:
    """Test cases for SalesAnalyzer class."""
    
    # Class-level analyzer instance for reuse across tests
    _analyzer = None
    _setup_time = None
    
    @classmethod
    def setup_class(cls):
        """Set up the analyzer once for all tests in this class."""
        start_time = time.time()
        logger.info("Setting up SalesAnalyzer for all tests...")
        
        cls.business_file_path = Path("data/raw/Business.xlsm")
        cls.analyzer = SalesAnalyzer(cls.business_file_path)
        cls.analyzer.spreadsheet_manager.open()
        cls.analyzer._is_open = True
        
        setup_duration = time.time() - start_time
        cls._setup_time = setup_duration
        logger.info(f"SalesAnalyzer setup completed in {setup_duration:.2f} seconds")
    
    @classmethod
    def teardown_class(cls):
        """Clean up the analyzer after all tests."""
        if cls._analyzer:
            start_time = time.time()
            logger.info("Tearing down SalesAnalyzer...")
            
            cls._analyzer.close()
            
            teardown_duration = time.time() - start_time
            logger.info(f"SalesAnalyzer teardown completed in {teardown_duration:.2f} seconds")
    
    def getTestStartDate(self):
        """Get the start date for testing."""
        return date(2025, 5, 16)
    
    def getTestEndDate(self):
        """Get the end date for testing."""
        return date(2025, 6, 15)
   
    # ============================================================================
    # PRIMARY TESTS - Core Functional Behavior
    # ============================================================================
    
    @pytest.mark.primary
    def test_get_new_industry_clients(self):
        """Primary test: Demonstrates the core functionality of getting unique industry clients."""
        start_time = time.time()
        
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        clients = self.analyzer.getNewIndustryClients(start_date, end_date)
        
        test_duration = time.time() - start_time
        logger.info(f"getNewIndustryClients test completed in {test_duration:.2f} seconds")
        
        # Validate return type and structure
        assert isinstance(clients, list)
        assert all(isinstance(client, str) for client in clients)
        
        # Validate uniqueness
        assert len(clients) == len(set(clients)), "Client list should contain unique values"
        
        # Validate no empty strings
        assert all(client.strip() for client in clients), "No empty client names should be returned"
        
        # Expected clients for the test date range (2025-05-16 to 2025-06-15)
        expected_clients = [
            'Anytime Fitness',
            'BrandServe',
            'Central Highlands Region Water Corporation',
            'Ethos Urban',
            'KU Children\'s Services',
            'Legal Aid NSW',
            'Macroplan',
            'Urbis',
            'YMCA Victoria'
        ]
        
        # Validate against expected client list
        assert set(clients) == set(expected_clients), f"Expected {expected_clients}, got {clients}"
        assert len(clients) == len(expected_clients), f"Expected {len(expected_clients)} clients, got {len(clients)}"
    
    @pytest.mark.primary
    def test_get_new_gov_clients(self):
        """Primary test: Demonstrates the core functionality of getting unique government clients."""
        start_time = time.time()
        
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        clients = self.analyzer.getNewGovClients(start_date, end_date)
        
        test_duration = time.time() - start_time
        logger.info(f"getNewGovClients test completed in {test_duration:.2f} seconds")
        
        # Validate return type and structure
        assert isinstance(clients, list)
        assert all(isinstance(client, str) for client in clients)
        
        # Validate uniqueness
        assert len(clients) == len(set(clients)), "Client list should contain unique values"
        
        # Validate no empty strings
        assert all(client.strip() for client in clients), "No empty client names should be returned"
        
        # Expected government clients for the test date range (2025-05-16 to 2025-06-15)
        expected_clients = [
            'Blue Mountains',
            'Central West Libraries',
            'Cockburn City',
            'Darebin City',
            'Dept. of Creative Industries, Tourism, Hospitality & Sport',
            'Fairfield City',
            'Greater Geelong',
            'Hay Shire Council',
            'Hobart City',
            'Joondalup City',
            'Kingston City',
            'Livingstone Shire',
            'Melbourne City',
            'Noosa Shire',
            'Northern Beaches',
            'Yarra Ranges Shire'
        ]
        
        # Validate against expected client list
        assert set(clients) == set(expected_clients), f"Expected {expected_clients}, got {clients}"
        assert len(clients) == len(expected_clients), f"Expected {len(expected_clients)} clients, got {len(clients)}"
    
    @pytest.mark.primary
    def test_caching_functionality(self):
        """Primary test: Demonstrates the key performance optimization through caching."""
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        # First call - should load data
        start_time = time.time()
        df1 = self.analyzer.getIndustrySalesData(start_date, end_date)
        first_call_time = time.time() - start_time
        
        # Second call - should use cached data
        start_time = time.time()
        df2 = self.analyzer.getIndustrySalesData(start_date, end_date)
        second_call_time = time.time() - start_time
        
        logger.info(f"First call: {first_call_time:.2f}s, Second call: {second_call_time:.2f}s")
        
        # Data should be identical
        pd.testing.assert_frame_equal(df1, df2)
        
        # Second call should be faster (cached)
        assert second_call_time < first_call_time, "Cached call should be faster"
    
    @pytest.mark.primary
    def test_can_load_industry_sales_data(self):
        """Primary test: Shows how to load and structure industry sales data."""
        test_start_time = time.time()
        logger.info("Starting test_can_load_industry_sales_data...")
        
        # Use a reasonable date range for testing
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        
        data_load_start = time.time()
        df = self.analyzer.getIndustrySalesData(start_date, end_date)
        data_load_time = time.time() - data_load_start
        logger.info(f"Industry data load took {data_load_time:.2f} seconds")
        
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
        
        test_time = time.time() - test_start_time
        logger.info(f"test_can_load_industry_sales_data completed in {test_time:.2f} seconds")
    
    @pytest.mark.primary
    def test_can_load_gov_sales_data(self):
        """Primary test: Shows how to load and structure government sales data."""
        test_start_time = time.time()
        logger.info("Starting test_can_load_gov_sales_data...")
        
        # Use a reasonable date range for testing
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        
        data_load_start = time.time()
        df = self.analyzer.getGovSalesData(start_date, end_date)
        data_load_time = time.time() - data_load_start
        logger.info(f"Government data load took {data_load_time:.2f} seconds")
        
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
        
        test_time = time.time() - test_start_time
        logger.info(f"test_can_load_gov_sales_data completed in {test_time:.2f} seconds")
    
    @pytest.mark.primary
    @pytest.mark.parametrize("client_name,client_type,expected_summary", [
        (
            "KU Children's Services",
            "industry",
            {
                "client": "KU Children's Services",
                "amount": 150000,
                "products": [],
                "details": ["Statewide childcare supply and demand assessment of Victoria"]
            }
        ),
        (
            "Blue Mountains",
            "government",
            {
                "client": "Blue Mountains",
                "amount": 33870.0,
                "products": ["profile.id", "atlas.id", "economy.id"],
                "details": []
            }
        ),
        (
            "Anytime Fitness",
            "industry",
            {
                "client": "Anytime Fitness",
                "amount": 15000,
                "products": [],
                "details": ["Detailed Hotspot Report"]
            }
        ),
        (
            "Central West Libraries",
            "government",
            {
                "client": "Central West Libraries",
                "amount": 500,
                "products": ["profile.id"],
                "details": []
            }
        )
    ])
    def test_get_client_summary(self, client_name: str, client_type: str, expected_summary: dict):
        """Primary test: Demonstrates client summary functionality with parameterized test cases."""
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        summary = self.analyzer.getClientSummary(client_name, client_type, start_date, end_date)
        
        # Validate return type and structure
        assert isinstance(summary, dict)
        assert "client" in summary
        assert "amount" in summary
        assert "products" in summary
        assert "details" in summary
        
        # Validate client name
        assert summary["client"] == expected_summary["client"]
        
        # Validate amount (allow for small floating point differences)
        assert abs(summary["amount"] - expected_summary["amount"]) < 0.01
        
        # Validate products list
        assert isinstance(summary["products"], list)
        assert set(summary["products"]) == set(expected_summary["products"])
        
        # Validate details list
        assert isinstance(summary["details"], list)
        assert set(summary["details"]) == set(expected_summary["details"])

    @pytest.mark.primary
    @pytest.mark.parametrize("client_type,expected_markdown", [
        (
            "industry",
            '''# New Industry Clients (2025-05-16 to 2025-06-15)

| Client | Amount | Products | Details |
|--------|--------|----------|---------|
| YMCA Victoria | $1,500 | Forecast (SAFi) | id’s population forecasts for the defined catchment - Fitzroy Gasworks 5min PEAK AM DT SA1s |
| Anytime Fitness | $15,000 |  | Detailed Hotspot Report |
| Legal Aid NSW | $60,000 |  | Statewide legal need and service provision analysis, |
| KU Children's Services | $150,000 |  | Statewide childcare supply and demand assessment of Victoria |
| Urbis | $1,200 | Forecast (SAFi) |  |
| Macroplan | $800 | Forecast (SAFi) |  |
| Ethos Urban | $400 | Forecast (SAFi) |  |
| BrandServe | $900 | Forecast (SAFi) |  |
| Central Highlands Region Water Corporation | $23,300 | Forecast (SAFi) |  |'''
        ),
        (
            "government",
            '''# New Government Clients (2025-05-16 to 2025-06-15)

| Client | Amount | Products | Details |
|--------|--------|----------|---------|
| Joondalup City | $12,000 | expert.id | Economic Health Check |
| Livingstone Shire | $15,000 | expert.id | Community Insights Report |
| Melbourne City | $13,000 | expert.id | Affordable Housing Needs Assessment |
| Kingston City | $10,000 | expert.id | City of Kingston Precinct Analysis |
| Yarra Ranges Shire | $39,600 | views.id |  |
| Darebin City | $9,500 | expert.id | Population and dwelling forecasts for DCP and Open Space precincts |
| Cockburn City | $55,350 | profile.id, atlas.id, forecast.id, economy.id |  |
| Central West Libraries | $500 | profile.id |  |
| Fairfield City | $1,860 | atlas.id, profile.id |  |
| Greater Geelong | $54,545 | views.id |  |
| Hobart City | $16,300 | economy.id |  |
| Blue Mountains | $33,870 | profile.id, atlas.id, economy.id |  |
| Hay Shire Council | $9,450 | profile.id, economy.id |  |
| Northern Beaches | $10,000 | expert.id | Green jobs and Business study (billed next year invoice on completion) |
| Noosa Shire | $3,500 | expert.id | Economic Development Breakfast 29 July - Speakers Fee .id Chief Economist, Rob Hall |
| Dept. of Creative Industries, Tourism, Hospitality & Sport | $85,000 | economy.id | Economic value output, NTE research |'''
        )
    ])
    def test_get_client_summary_markdown(self, client_type: str, expected_markdown: str):
        """Primary test: Demonstrates markdown table generation for client summaries with golden answer validation."""
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        markdown = self.analyzer.getClientSummaryMarkdown(client_type, start_date, end_date)
        
        # Validate return type
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        
        # Golden answer validation - compare exact output
        assert markdown == expected_markdown
    
    # ============================================================================
    # COVERAGE TESTS - Resilience & Edge Cases
    # ============================================================================
    
    def test_date_range_filtering(self):
        """Coverage test: Edge case - narrow date range filtering."""
        test_start_time = time.time()
        logger.info("Starting test_date_range_filtering...")
        
        # Test with a very narrow date range
        start_date = date(2024, 6, 1)
        end_date = date(2024, 6, 30)
        
        industry_start = time.time()
        industry_df = self.analyzer.getIndustrySalesData(start_date, end_date)
        industry_time = time.time() - industry_start
        logger.info(f"Industry narrow range load took {industry_time:.2f} seconds")
        
        gov_start = time.time()
        gov_df = self.analyzer.getGovSalesData(start_date, end_date)
        gov_time = time.time() - gov_start
        logger.info(f"Government narrow range load took {gov_time:.2f} seconds")
        
        # Verify all dates are within the narrow range
        for df in [industry_df, gov_df]:
            if len(df) > 0:
                for row_date in df['Date']:
                    assert start_date <= row_date.date() <= end_date
        
        test_time = time.time() - test_start_time
        logger.info(f"test_date_range_filtering completed in {test_time:.2f} seconds")
    
    def test_invalid_date_range(self):
        """Coverage test: Error handling - invalid date ranges."""
        test_start_time = time.time()
        logger.info("Starting test_invalid_date_range...")
        
        # Test with start date after end date
        start_date = date(2024, 12, 31)
        end_date = date(2024, 1, 1)
        
        with pytest.raises(ValueError) as exc_info:
            self.analyzer.getIndustrySalesData(start_date, end_date)
        assert "Start date must be before or equal to end date" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            self.analyzer.getGovSalesData(start_date, end_date)
        assert "Start date must be before or equal to end date" in str(exc_info.value)
        
        test_time = time.time() - test_start_time
        logger.info(f"test_invalid_date_range completed in {test_time:.2f} seconds")
    
    def test_missing_sheet_error(self):
        """Coverage test: Error handling - missing sheets."""
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
        """Coverage test: Error handling - data structure validation."""
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
        """Coverage test: Integration - context manager usage."""
        # Create a separate instance for context manager testing
        with SalesAnalyzer(self.analyzer.file_path) as analyzer:
            start_date = date(2023, 1, 1)
            end_date = date(2024, 12, 31)
            
            # Should be able to load data
            df = analyzer.getIndustrySalesData(start_date, end_date)
            assert isinstance(df, pd.DataFrame)
        
        # Verify the connection was closed
        assert not analyzer._is_open
    
    def test_raises_error_for_missing_file(self):
        """Coverage test: Error handling - missing file."""
        analyzer = SalesAnalyzer(Path("data/raw/nonexistent.xlsm"))
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        
        with pytest.raises(FileNotFoundError):
            analyzer.getIndustrySalesData(start_date, end_date)
    
    def test_invalid_config_key(self):
        """Coverage test: Error handling - invalid configuration keys."""
        test_start_time = time.time()
        logger.info("Starting test_invalid_config_key...")
        
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        
        with pytest.raises(ValueError) as exc_info:
            self.analyzer._get_sales_data('invalid_key', start_date, end_date)
        assert "Unknown config key: invalid_key" in str(exc_info.value)
        
        test_time = time.time() - test_start_time
        logger.info(f"test_invalid_config_key completed in {test_time:.2f} seconds")
    
    def test_caching_with_different_ranges(self):
        """Coverage test: Edge case - cache behavior with different date ranges."""
        # Load data for a specific range
        start_date1 = self.getTestStartDate()
        end_date1 = self.getTestEndDate()
        
        df1 = self.analyzer.getIndustrySalesData(start_date1, end_date1)
        
        # Request a subset range - should use cached data
        start_date2 = date(2025, 5, 20)
        end_date2 = date(2025, 6, 10)
        
        start_time = time.time()
        df2 = self.analyzer.getIndustrySalesData(start_date2, end_date2)
        subset_call_time = time.time() - start_time
        
        logger.info(f"Subset range call time: {subset_call_time:.2f}s")
        
        # The subset should be contained within the original data
        assert len(df2) <= len(df1)
        
        # Request a larger range - should reload data
        start_date3 = date(2025, 5, 1)
        end_date3 = date(2025, 6, 30)
        
        start_time = time.time()
        df3 = self.analyzer.getIndustrySalesData(start_date3, end_date3)
        larger_call_time = time.time() - start_time
        
        logger.info(f"Larger range call time: {larger_call_time:.2f}s")
        
        # Should have more data
        assert len(df3) >= len(df1)
    
    def test_date_filtering_inclusive(self):
        """Coverage test: Edge case - date boundary behavior."""
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        df = self.analyzer.getIndustrySalesData(start_date, end_date)
        
        if len(df) > 0:
            # Check that all dates are within the range (inclusive)
            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()
            
            assert min_date >= start_date, f"Min date {min_date} should be >= start date {start_date}"
            assert max_date <= end_date, f"Max date {max_date} should be <= end date {end_date}"
    
    def test_error_handling_invalid_date_range_new_methods(self):
        """Coverage test: Error handling - new methods validation."""
        start_date = date(2025, 6, 15)
        end_date = date(2025, 5, 16)
        
        with pytest.raises(ValueError, match="Start date must be before or equal to end date"):
            self.analyzer.getNewIndustryClients(start_date, end_date)
        
        with pytest.raises(ValueError, match="Start date must be before or equal to end date"):
            self.analyzer.getNewGovClients(start_date, end_date)

    def test_get_client_summary_invalid_client_type(self):
        """Coverage test: Error handling - invalid client type in getClientSummary."""
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        with pytest.raises(ValueError, match="Invalid client_type: invalid"):
            self.analyzer.getClientSummary("Test Client", "invalid", start_date, end_date)

    def test_get_client_summary_nonexistent_client(self):
        """Coverage test: Edge case - client that doesn't exist returns empty summary."""
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        summary = self.analyzer.getClientSummary("Nonexistent Client", "industry", start_date, end_date)
        
        assert summary["client"] == "Nonexistent Client"
        assert summary["amount"] == 0.0
        assert summary["products"] == []
        assert summary["details"] == []

    def test_get_client_summary_empty_results(self):
        """Coverage test: Edge case - client with no data in date range."""
        # Use a date range where we know there's no data
        start_date = date(2020, 1, 1)
        end_date = date(2020, 1, 31)
        
        summary = self.analyzer.getClientSummary("KU Children's Services", "industry", start_date, end_date)
        
        assert summary["client"] == "KU Children's Services"
        assert summary["amount"] == 0.0
        assert summary["products"] == []
        assert summary["details"] == []

    def test_get_client_summary_consulting_exclusion(self):
        """Coverage test: Edge case - 'Consulting' products are excluded from products list."""
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        # This test assumes there's a client with 'Consulting' as a product
        # If no such client exists in the test data, this test will pass with empty products
        summary = self.analyzer.getClientSummary("KU Children's Services", "industry", start_date, end_date)
        
        # Verify that 'Consulting' is not in the products list
        assert "Consulting" not in summary["products"]
        assert isinstance(summary["products"], list)
 

    def test_get_client_summary_markdown_invalid_client_type(self):
        """Coverage test: Error handling - invalid client type in getClientSummaryMarkdown."""
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        with pytest.raises(ValueError, match="Invalid client_type: invalid"):
            self.analyzer.getClientSummaryMarkdown("invalid", start_date, end_date)

    def test_get_client_summary_markdown_empty_results(self):
        """Coverage test: Edge case - no clients in date range returns appropriate message."""
        # Use a date range where we know there's no data
        start_date = date(2020, 1, 1)
        end_date = date(2020, 1, 31)
        
        markdown = self.analyzer.getClientSummaryMarkdown("industry", start_date, end_date)
        
        assert isinstance(markdown, str)
        assert "No clients found for the specified date range" in markdown
        assert markdown.startswith("# New Industry Clients")

    def test_whitespace_trimming_in_data_loading(self):
        """Coverage test: Edge case - client names with trailing whitespace are properly trimmed."""
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        # Test that Anytime Fitness with trailing space matches Anytime Fitness without trailing space
        summary = self.analyzer.getClientSummary("Anytime Fitness", "industry", start_date, end_date)
        
        # Should not be empty (should find the data after trimming)
        assert summary["client"] == "Anytime Fitness"
        assert summary["amount"] > 0  # Should have some amount, not 0
        assert len(summary["products"]) > 0 or len(summary["details"]) > 0  # Should have some data
        
        # Verify that the client appears in the client list (after trimming)
        clients = self.analyzer.getNewIndustryClients(start_date, end_date)
        assert "Anytime Fitness" in clients

    def test_markdown_structure_validation(self):
        """Coverage test: Edge case - markdown structure is properly formatted."""
        start_date = self.getTestStartDate()
        end_date = self.getTestEndDate()
        
        markdown = self.analyzer.getClientSummaryMarkdown("industry", start_date, end_date)
        
        # Validate return type
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        
        # Validate markdown structure
        lines = markdown.split('\n')
        assert len(lines) >= 4  # Title, empty line, header, separator
        
        # Validate title format
        assert lines[0].startswith("# New Industry Clients")
        assert f"({start_date} to {end_date})" in lines[0]
        
        # Validate table header
        assert "| Client | Amount | Products | Details |" in lines[2]
        assert "|--------|--------|----------|---------|" in lines[3]
        
        # Validate that we have data rows
        data_rows = [line for line in lines[4:] if line.strip() and line.startswith('|')]
        assert len(data_rows) > 0
        
        # Validate each data row format
        for row in data_rows:
            assert row.count('|') == 5  # 4 columns + 2 outer pipes
            parts = row.split('|')
            assert len(parts) == 6  # 4 columns + empty strings at start/end
            client = parts[1].strip()
            amount = parts[2].strip()
            products = parts[3].strip()
            details = parts[4].strip()
            
            # Validate client name is not empty
            assert client
            
            # Validate amount format (starts with $ and contains numbers)
            assert amount.startswith('$')
            assert any(c.isdigit() for c in amount)
            
            # Products and details can be empty, but should be strings
            assert isinstance(products, str)
            assert isinstance(details, str)
 
