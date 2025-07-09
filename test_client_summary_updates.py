#!/usr/bin/env python3
"""Check which client summaries need to be updated due to new filtering logic."""

from datetime import date
from src.tool_experiments.sales_analyzer import SalesAnalyzer

def check_client_summaries():
    """Check client summaries that need updating."""
    print("Checking client summaries for updates...")
    
    analyzer = SalesAnalyzer()
    
    # Test date range
    start_date = date(2025, 5, 16)
    end_date = date(2025, 6, 15)
    
    # Test clients from the parameterized test
    test_clients = [
        ("KU Children's Services", "industry"),
        ("Blue Mountains", "government"),
        ("Anytime Fitness", "industry"),
        ("Central West Libraries", "government")
    ]
    
    try:
        for client_name, client_type in test_clients:
            print(f"\n=== {client_name} ({client_type}) ===")
            try:
                summary = analyzer.getClientSummary(client_name, client_type, start_date, end_date)
                print(f"Amount: ${summary['amount']:,.0f}")
                print(f"Products: {summary['products']}")
                print(f"Details: {summary['details']}")
                print(f"Summary dict: {summary}")
            except Exception as e:
                print(f"Error or client not found: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    check_client_summaries() 