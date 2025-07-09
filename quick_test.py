from datetime import date
from src.tool_experiments.sales_analyzer import SalesAnalyzer

a = SalesAnalyzer()
markdown = a.getClientSummaryMarkdown('industry', date(2025,5,16), date(2025,6,15))
print("Test passed" if "Sale Type" in markdown else "Test failed")
a.close() 