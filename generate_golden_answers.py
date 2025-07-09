#!/usr/bin/env python3
"""Generate new golden answers for markdown test with filtered data."""

from datetime import date
from src.tool_experiments.sales_analyzer import SalesAnalyzer

def generate_golden_answers():
    """Generate new golden answers for the markdown test."""
    print("Generating new golden answers...")
    
    analyzer = SalesAnalyzer()
    
    # Test date range (same as test)
    start_date = date(2025, 5, 16)
    end_date = date(2025, 6, 15)
    
    try:
        # Generate industry markdown
        print("\n=== Industry Markdown ===")
        industry_markdown = analyzer.getClientSummaryMarkdown("industry", start_date, end_date)
        print("INDUSTRY_GOLDEN_ANSWER = '''")
        print(industry_markdown)
        print("'''")
        
        # Generate government markdown
        print("\n=== Government Markdown ===")
        gov_markdown = analyzer.getClientSummaryMarkdown("government", start_date, end_date)
        print("GOVERNMENT_GOLDEN_ANSWER = '''")
        print(gov_markdown)
        print("'''")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    generate_golden_answers() 