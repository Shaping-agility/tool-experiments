from pathlib import Path
from datetime import date, datetime
from calendar import monthrange
from typing import Optional
from .sales_analyzer import SalesAnalyzer
from .sales_lead_analyzer import SalesLeadAnalyzer
from .chat_thread_loader import EmailChatThreadLoader


class MonthlySummaryProducer:
    """Produces monthly summary documents by packaging existing analyzer functionality."""
    
    def __init__(self):
        """Initialize the MonthlySummaryProducer."""
        self.processed_dir = Path("data/processed")
        self.raw_dir = Path("data/raw")
        
        # Ensure processed directory exists
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, month: int, year: Optional[int] = None) -> None:
        """Generate monthly summary documents for the specified month/year.
        
        Args:
            month: Month number (1-12)
            year: Year (defaults to current year if not specified)
            
        Raises:
            ValueError: If month is invalid (not 1-12)
            RuntimeError: If any component fails during generation
        """
        if not 1 <= month <= 12:
            raise ValueError(f"Invalid month: {month}. Must be between 1 and 12.")
        
        if year is None:
            year = datetime.now().year
        
        print(f"Generating monthly summaries for {self._get_month_name(month)} {year}...")
        
        # Calculate date range
        start_date, end_date = self._calculate_date_range(month, year)
        print(f"Date range: {start_date} to {end_date}")
        
        try:
            # Generate sales summary
            print("Generating sales summary...")
            sales_content = self._generate_sales_summary(start_date, end_date)
            sales_filename = f"Sales Summary {self._get_month_name(month)} {year}.md"
            self._write_file(sales_filename, sales_content)
            print(f"✓ Sales summary written to {sales_filename}")
            
            # Generate leads summary
            print("Generating leads summary...")
            leads_content = self._generate_leads_summary()
            leads_filename = f"Sales Lead Summary {self._get_month_name(month)} {year}.md"
            self._write_file(leads_filename, leads_content)
            print(f"✓ Leads summary written to {leads_filename}")
            
            # Generate chat threads summary
            print("Generating chat threads summary...")
            chat_content = self._generate_chat_threads_summary(start_date, end_date)
            chat_filename = f"Chat Threads {self._get_month_name(month)} {year}.md"
            self._write_file(chat_filename, chat_content)
            print(f"✓ Chat threads summary written to {chat_filename}")
            
            print(f"\n✓ All summaries generated successfully for {self._get_month_name(month)} {year}")
            
        except Exception as e:
            print(f"✗ Error generating summaries: {e}")
            raise RuntimeError(f"Failed to generate monthly summaries: {e}")
    
    def _calculate_date_range(self, month: int, year: int) -> tuple[date, date]:
        """Calculate first and last day of the specified month.
        
        Args:
            month: Month number (1-12)
            year: Year
            
        Returns:
            Tuple of (start_date, end_date) for the month
        """
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        return start_date, end_date
    
    def _get_month_name(self, month: int) -> str:
        """Get abbreviated month name.
        
        Args:
            month: Month number (1-12)
            
        Returns:
            Abbreviated month name (Jan, Feb, etc.)
        """
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        return month_names[month - 1]
    
    def _generate_sales_summary(self, start_date: date, end_date: date) -> str:
        """Generate sales summary markdown using existing SalesAnalyzer methods.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            Markdown formatted string with sales summary
        """
        analyzer = SalesAnalyzer()
        
        try:
            # Generate industry and government summaries
            industry_markdown = analyzer.getClientSummaryMarkdown("industry", start_date, end_date)
            government_markdown = analyzer.getClientSummaryMarkdown("government", start_date, end_date)
            
            # Combine into comprehensive summary
            combined_markdown = f"# Sales Summary\n\n"
            combined_markdown += f"**Period:** {start_date} to {end_date}\n\n"
            combined_markdown += f"## Industry Sales\n\n{industry_markdown}\n\n"
            combined_markdown += f"## Government Sales\n\n{government_markdown}"
            
            return combined_markdown
            
        finally:
            analyzer.close()
    
    def _generate_leads_summary(self) -> str:
        """Generate leads summary markdown using existing SalesLeadAnalyzer methods.
        
        Returns:
            Markdown formatted string with leads summary
        """
        analyzer = SalesLeadAnalyzer(sheet_name="All deals")
        
        try:
            analyzer.load_data()
            return analyzer.getSummaryMarkdown()
        finally:
            analyzer.close()
    
    def _generate_chat_threads_summary(self, start_date: date, end_date: date) -> str:
        """Generate chat threads summary markdown using existing ChatThread methods.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            Markdown formatted string with chat threads summary
        """
        loader = EmailChatThreadLoader()
        
        # Load all threads
        threads = loader.load_threadList(str(self.raw_dir / "*.eml"))
        
        # Filter threads by date metadata
        qualifying_threads = []
        for thread in threads:
            thread_date = self._parse_thread_date(thread.get_metadata()['date'])
            if thread_date and start_date <= thread_date <= end_date:
                qualifying_threads.append(thread)
        
        if not qualifying_threads:
            return f"# Chat Threads Summary\n\n**Period:** {start_date} to {end_date}\n\nNo chat threads found for this period."
        
        # Generate markdown for qualifying threads
        markdown_lines = [f"# Chat Threads Summary\n\n**Period:** {start_date} to {end_date}\n\n"]
        
        for i, thread in enumerate(qualifying_threads):
            if i > 0:
                markdown_lines.append("\n\n---\n\n")
            markdown_lines.append(thread.to_markdown())
        
        return "".join(markdown_lines)
    
    def _parse_thread_date(self, date_str: str) -> Optional[date]:
        """Parse thread date string to date object.
        
        Args:
            date_str: Date string from thread metadata
            
        Returns:
            Parsed date or None if parsing fails
        """
        try:
            # Try to parse common email date formats
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.date()
        except (ValueError, TypeError):
            # If parsing fails, return None
            return None
    
    def _write_file(self, filename: str, content: str) -> None:
        """Write content to file in data/processed directory.
        
        Args:
            filename: Name of the file to write
            content: Content to write to the file
            
        Raises:
            RuntimeError: If file cannot be written
        """
        file_path = self.processed_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise RuntimeError(f"Failed to write file {filename}: {e}") 