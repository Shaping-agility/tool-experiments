#!/usr/bin/env python3
"""Simple test script to verify new business filtering logic."""

from datetime import date
from src.tool_experiments.sales_analyzer import SalesAnalyzer

def test_new_filtering():
    """Test the new business filtering logic."""
    print("Testing new business filtering logic...")
    
    analyzer = SalesAnalyzer()
    
    # Test date range
    start_date = date(2025, 5, 16)
    end_date = date(2025, 6, 15)
    
    try:
        # Test industry clients
        print("\n=== Industry Clients ===")
        industry_clients = analyzer.getNewIndustryClients(start_date, end_date)
        print(f"Industry clients (filtered): {len(industry_clients)}")
        print(f"First 5 clients: {industry_clients[:5]}")
        
        # Test government clients
        print("\n=== Government Clients ===")
        gov_clients = analyzer.getNewGovClients(start_date, end_date)
        print(f"Government clients (filtered): {len(gov_clients)}")
        print(f"First 5 clients: {gov_clients[:5]}")
        
        # Test a specific client summary
        if industry_clients:
            test_client = industry_clients[0]
            print(f"\n=== Client Summary for {test_client} ===")
            summary = analyzer.getClientSummary(test_client, "industry", start_date, end_date)
            print(f"Amount: ${summary['amount']:,.0f}")
            print(f"Products: {summary['products']}")
            print(f"Details: {summary['details']}")
        
        # Test markdown generation
        print("\n=== Markdown Generation ===")
        industry_markdown = analyzer.getClientSummaryMarkdown("industry", start_date, end_date)
        print(f"Industry markdown length: {len(industry_markdown)}")
        print("First 500 chars:")
        print(industry_markdown[:500])
        
        gov_markdown = analyzer.getClientSummaryMarkdown("government", start_date, end_date)
        print(f"\nGovernment markdown length: {len(gov_markdown)}")
        print("First 500 chars:")
        print(gov_markdown[:500])
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    test_new_filtering() 