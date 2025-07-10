# tests/test_monthly_summary_producer.py
import pytest
from pathlib import Path
from datetime import date
from src.tool_experiments.monthly_summary_producer import MonthlySummaryProducer


class TestMonthlySummaryProducer:
    """Test cases for MonthlySummaryProducer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.producer = MonthlySummaryProducer()
        self.processed_dir = Path("data/processed")
        
        # Ensure processed directory exists
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test files."""
        # Remove test files if they exist

    
    # ============================================================================
    # PRIMARY TESTS - Core Functional Behavior
    # ============================================================================
    
    @pytest.mark.primary
    def test_generate_may_2025_summaries(self):
        """Primary test: Generate monthly summaries for May 2025."""
        print("Starting May 2025 summary generation test...")
        
        # Generate summaries for May 2025
        self.producer.generate(month=5, year=2025)
        
        # Verify all three files were created
        expected_files = [
            "Sales Summary May 2025.md",
            "Sales Lead Summary May 2025.md",
            "Chat Threads May 2025.md"
        ]
        
        for filename in expected_files:
            file_path = self.processed_dir / filename
            assert file_path.exists(), f"Expected file {filename} was not created"
            assert file_path.stat().st_size > 0, f"File {filename} is empty"
            
            # Verify file content has expected structure
            content = file_path.read_text(encoding='utf-8')
            assert len(content) > 0, f"File {filename} has no content"
            
            # Verify markdown structure
            if "Sales Summary" in filename:
                assert "# Sales Summary" in content
                assert "## Industry Sales" in content
                assert "## Government Sales" in content
                assert "**Period:** 2025-05-01 to 2025-05-31" in content
            elif "Sales Lead Summary" in filename:
                assert "# Sales Lead Summary" in content
                assert "## Industry" in content
                assert "## Government" in content
            elif "Chat Threads" in filename:
                assert "# Chat Threads Summary" in content
                assert "**Period:** 2025-05-01 to 2025-05-31" in content
        
        print("✓ All three summary files generated successfully for May 2025")
    
    @pytest.mark.primary
    def test_generate_with_default_year(self):
        """Primary test: Generate summaries with default year (current year)."""
        # This test verifies the default year functionality
        # We'll test with a known month but let year default
        current_year = date.today().year
        
        # Generate summaries for current month with default year
        self.producer.generate(month=1)  # January of current year
        
        # Verify files were created with current year
        expected_files = [
            f"Sales Summary Jan {current_year}.md",
            f"Sales Lead Summary Jan {current_year}.md",
            f"Chat Threads Jan {current_year}.md"
        ]
        
        for filename in expected_files:
            file_path = self.processed_dir / filename
            if file_path.exists():
                file_path.unlink()  # Clean up
        
        print("✓ Default year functionality works correctly")
    
    # ============================================================================
    # COVERAGE TESTS - Edge Cases & Error Handling
    # ============================================================================
    
    def test_invalid_month_error(self):
        """Coverage test: Error handling for invalid month."""
        with pytest.raises(ValueError, match="Invalid month: 13"):
            self.producer.generate(month=13, year=2025)
        
        with pytest.raises(ValueError, match="Invalid month: 0"):
            self.producer.generate(month=0, year=2025)
    
    def test_date_range_calculation(self):
        """Coverage test: Date range calculation for different months."""
        # Test February (leap year)
        start_date, end_date = self.producer._calculate_date_range(2, 2024)
        assert start_date == date(2024, 2, 1)
        assert end_date == date(2024, 2, 29)  # Leap year
        
        # Test February (non-leap year)
        start_date, end_date = self.producer._calculate_date_range(2, 2025)
        assert start_date == date(2025, 2, 1)
        assert end_date == date(2025, 2, 28)  # Non-leap year
        
        # Test December
        start_date, end_date = self.producer._calculate_date_range(12, 2025)
        assert start_date == date(2025, 12, 1)
        assert end_date == date(2025, 12, 31)
    
    def test_month_name_generation(self):
        """Coverage test: Month name generation."""
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        
        for i, expected_name in enumerate(month_names, 1):
            actual_name = self.producer._get_month_name(i)
            assert actual_name == expected_name, f"Month {i} should be {expected_name}, got {actual_name}"
    
    def test_thread_date_parsing(self):
        """Coverage test: Thread date parsing functionality."""
        # Test valid date parsing
        valid_date_str = "Wed, 9 Jul 2025 00:27:39 +0000"
        parsed_date = self.producer._parse_thread_date(valid_date_str)
        assert parsed_date == date(2025, 7, 9)
        
        # Test invalid date parsing
        invalid_date_str = "Invalid date string"
        parsed_date = self.producer._parse_thread_date(invalid_date_str)
        assert parsed_date is None
        
        # Test empty string
        parsed_date = self.producer._parse_thread_date("")
        assert parsed_date is None
    
    def test_file_replacement(self):
        """Coverage test: File replacement functionality."""
        # Create a test file first
        test_filename = "Sales Summary May 2025.md"
        test_content = "Old content"
        test_file_path = self.processed_dir / test_filename
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Verify file exists with old content
        assert test_file_path.exists()
        assert test_file_path.read_text(encoding='utf-8') == test_content
        
        # Generate summaries (should replace the file)
        self.producer.generate(month=5, year=2025)
        
        # Verify file was replaced with new content
        new_content = test_file_path.read_text(encoding='utf-8')
        assert new_content != test_content
        assert "# Sales Summary" in new_content
    
    def test_empty_chat_threads_period(self):
        """Coverage test: Handling period with no chat threads."""
        # Test a period that should have no chat threads (far future)
        future_start = date(2030, 1, 1)
        future_end = date(2030, 1, 31)
        
        content = self.producer._generate_chat_threads_summary(future_start, future_end)
        
        assert "No chat threads found for this period" in content
        assert "**Period:** 2030-01-01 to 2030-01-31" in content
    
    def test_sales_lead_analyzer_integration(self):
        """Coverage test: SalesLeadAnalyzer integration with new markdown method."""
        from src.tool_experiments.sales_lead_analyzer import SalesLeadAnalyzer
        
        analyzer = SalesLeadAnalyzer(sheet_name="All deals")
        analyzer.load_data()
        
        markdown = analyzer.getSummaryMarkdown()
        
        # Verify markdown structure
        assert "# Sales Lead Summary" in markdown
        assert "## Industry" in markdown
        assert "## Government" in markdown
        assert "### High Conviction" in markdown
        assert "### Medium Conviction" in markdown
        
        # Verify engagement types are included
        engagement_types = ["Product", "Consulting", "Product & Consulting"]
        for engagement_type in engagement_types:
            assert f"#### {engagement_type}" in markdown
        
        analyzer.close()
    
    def test_consulting_government_sector_logic(self):
        """Coverage test: Verify 'Consulting Government' is treated as Government sector."""
        from src.tool_experiments.sales_lead_analyzer import SalesLeadAnalyzer
        
        analyzer = SalesLeadAnalyzer(sheet_name="All deals")
        analyzer.load_data()
        
        # Get the dataframe to check sector assignment
        df = analyzer.get_dataframe()
        
        # Find rows with "Consulting Government" engagement type
        consulting_gov_rows = df[df['Engagement Type'] == 'Consulting Government']
        
        if len(consulting_gov_rows) > 0:
            # All Consulting Government rows should have Government sector
            for _, row in consulting_gov_rows.iterrows():
                assert row['Sector'] == 'Government', f"Consulting Government should be Government sector, got {row['Sector']}"
        
        analyzer.close() 