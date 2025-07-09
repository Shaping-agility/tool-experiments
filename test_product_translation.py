#!/usr/bin/env python3
"""Test the product translation functionality."""

from datetime import date
from src.tool_experiments.sales_analyzer import SalesAnalyzer

def test_product_translation():
    """Test the product translation functionality."""
    print("Testing product translation...")
    
    analyzer = SalesAnalyzer()
    
    # Test date range
    start_date = date(2025, 5, 16)
    end_date = date(2025, 6, 15)
    
    try:
        # Test specific clients to see product translations
        test_clients = [
            ("Blue Mountains", "government"),
            ("Cockburn City", "government"),
            ("Joondalup City", "government")
        ]
        
        for client_name, client_type in test_clients:
            print(f"\n=== {client_name} ({client_type}) ===")
            try:
                summary = analyzer.getClientSummary(client_name, client_type, start_date, end_date)
                print(f"Amount: ${summary['amount']:,.0f}")
                print(f"Products: {summary['products']}")
                print(f"Sale Type: {summary['sale_type']}")
            except Exception as e:
                print(f"Error: {e}")
        
        # Test markdown generation to see translated products
        print("\n=== Markdown Generation (first 1000 chars) ===")
        gov_markdown = analyzer.getClientSummaryMarkdown("government", start_date, end_date)
        print(gov_markdown[:1000])
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    test_product_translation() 