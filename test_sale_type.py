#!/usr/bin/env python3
"""Test the new sale type functionality."""

from datetime import date
from src.tool_experiments.sales_analyzer import SalesAnalyzer

def test_sale_type():
    """Test the sale type functionality."""
    print("Testing sale type functionality...")
    
    analyzer = SalesAnalyzer()
    
    # Test date range
    start_date = date(2025, 5, 16)
    end_date = date(2025, 6, 15)
    
    try:
        # Test a few client summaries to see the sale type
        test_clients = [
            ("Anytime Fitness", "industry"),
            ("Blue Mountains", "government"),
            ("Joondalup City", "government")
        ]
        
        for client_name, client_type in test_clients:
            print(f"\n=== {client_name} ({client_type}) ===")
            try:
                summary = analyzer.getClientSummary(client_name, client_type, start_date, end_date)
                print(f"Amount: ${summary['amount']:,.0f}")
                print(f"Sale Type: {summary['sale_type']}")
                print(f"Products: {summary['products']}")
                print(f"Details: {summary['details']}")
            except Exception as e:
                print(f"Error: {e}")
        
        # Test markdown generation
        print("\n=== Markdown Generation ===")
        industry_markdown = analyzer.getClientSummaryMarkdown("industry", start_date, end_date)
        print("Industry markdown (first 800 chars):")
        print(industry_markdown[:800])
        
        gov_markdown = analyzer.getClientSummaryMarkdown("government", start_date, end_date)
        print("\nGovernment markdown (first 800 chars):")
        print(gov_markdown[:800])
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    test_sale_type() 