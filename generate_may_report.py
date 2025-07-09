#!/usr/bin/env python3
"""Generate May.md report with industry and government client summaries."""

from datetime import date
from pathlib import Path
from src.tool_experiments.sales_analyzer import SalesAnalyzer

def generate_may_report():
    """Generate May.md report with both industry and government summaries."""
    print("Generating May.md report...")
    
    analyzer = SalesAnalyzer()
    
    # May 2025 date range
    start_date = date(2025, 5, 1)
    end_date = date(2025, 5, 31)
    
    try:
        # Generate industry markdown
        print("Generating industry markdown...")
        industry_markdown = analyzer.getClientSummaryMarkdown("industry", start_date, end_date)
        
        # Generate government markdown
        print("Generating government markdown...")
        government_markdown = analyzer.getClientSummaryMarkdown("government", start_date, end_date)
        
        # Create the output content
        output_content = f"""# May 2025 Client Summary Report

## Industry Clients

{industry_markdown}

## Government Clients

{government_markdown}
"""
        
        # Ensure output directory exists
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write to file
        output_file = output_dir / "May.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"Report generated successfully: {output_file}")
        print(f"File size: {output_file.stat().st_size} bytes")
        
    except Exception as e:
        print(f"Error generating report: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    generate_may_report() 