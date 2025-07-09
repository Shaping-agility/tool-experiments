#!/usr/bin/env python3
"""
Script to generate golden answers for markdown tests using SalesAnalyzer.
"""

from src.tool_experiments.sales_analyzer import SalesAnalyzer
from datetime import date

def generate_markdown_golden_answer(client_type: str, start_date: date, end_date: date) -> str:
    """Generate the exact markdown output for a given client type and date range."""
    analyzer = SalesAnalyzer()
    
    # Get all clients for the type
    if client_type == 'industry':
        clients = analyzer.getNewIndustryClients(start_date, end_date)
    else:
        clients = analyzer.getNewGovClients(start_date, end_date)
    
    # Generate title
    title = f"# New {client_type.title()} Clients ({start_date} to {end_date})"
    
    if not clients:
        return f"{title}\n\nNo clients found for the specified date range."
    
    # Build table header
    table_lines = [
        title,
        "",
        "| Client | Amount | Products | Details |",
        "|--------|--------|----------|---------|"
    ]
    
    # Build table rows
    for client_name in clients:
        summary = analyzer.getClientSummary(client_name, client_type, start_date, end_date)
        
        # Format the row
        client = summary['client']
        amount = f"${summary['amount']:,.0f}"
        products = ", ".join(summary['products']) if summary['products'] else ""
        details = " ".join(summary['details']) if summary['details'] else ""
        
        table_lines.append(f"| {client} | {amount} | {products} | {details} |")
    
    return "\n".join(table_lines)

def main():
    """Generate golden answers for both industry and government."""
    start_date = date(2025, 5, 16)
    end_date = date(2025, 6, 15)
    
    print("Generating golden answers for markdown tests...")
    
    # Generate industry golden answer
    print("Generating industry golden answer...")
    industry_markdown = generate_markdown_golden_answer('industry', start_date, end_date)
    
    # Generate government golden answer
    print("Generating government golden answer...")
    government_markdown = generate_markdown_golden_answer('government', start_date, end_date)
    
    # Write to file
    with open('golden_answers.txt', 'w') as f:
        f.write("INDUSTRY GOLDEN ANSWER:\n")
        f.write("=" * 50 + "\n")
        f.write(f'"""\n{industry_markdown}\n"""\n\n')
        f.write("GOVERNMENT GOLDEN ANSWER:\n")
        f.write("=" * 50 + "\n")
        f.write(f'"""\n{government_markdown}\n"""\n')
    
    print("Golden answers written to golden_answers.txt")
    print("Golden answers generated successfully!")

if __name__ == "__main__":
    main() 