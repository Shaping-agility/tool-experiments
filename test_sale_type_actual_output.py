#!/usr/bin/env python3
from datetime import date
from src.tool_experiments.sales_analyzer import SalesAnalyzer

def print_actual_markdown():
    analyzer = SalesAnalyzer()
    start_date = date(2025, 5, 16)
    end_date = date(2025, 6, 15)
    print('=== ACTUAL INDUSTRY MARKDOWN OUTPUT ===')
    print(analyzer.getClientSummaryMarkdown('industry', start_date, end_date))
    print('\n=== ACTUAL GOVERNMENT MARKDOWN OUTPUT ===')
    print(analyzer.getClientSummaryMarkdown('government', start_date, end_date))
    analyzer.close()

if __name__ == '__main__':
    print_actual_markdown() 