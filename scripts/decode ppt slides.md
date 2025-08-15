You are a data-savvy analyst. Two image slides are attached:

Slide 1 – FY KPI Dashboard
Grey tiles showing current YTD values plus prior-year comparators.

Slide 2 – Revenue Charts
Top chart = Revenue by Quarter with growth vs prior quarter (%).
Bottom chart = Revenue by Quarter with growth vs same quarter of prior year (%).
Q1 FY 2024 absolute revenue (“$ 2,519,000”) is stated on the slide.

Task
Produce only the following markdown blocks—no commentary:

Block A – KPI Table
A markdown table with these columns in order:

| Metric | Current Value | Previous Value | % Change |

Populate one row per tile on Slide 1 that has both a current and previous value.
Calculate % Change = (Current – Previous) ÷ Previous, rounded to 1 decimal place and shown with “+”/“–”.

Block B – One-off Listings
List any metrics from Slide 1 that don’t fit the table format (e.g., ratios, multi-number strings).
Show each on its own bullet, exactly as displayed, with no interpretation.

Block C – Quarterly Revenue Table
Derive absolute revenue for every quarter FY 2024 and FY 2025:

Use Q1 FY 2024 revenue ($ 2,519,000) as the base.

Apply the top-chart quarter-over-quarter % moves sequentially to compute:

Q2, Q3, Q4 of FY 2024.

Q1–Q4 of FY 2025 (start from FY 2024 Q4, then apply FY 2025 q-o-q %).

Round each revenue figure to the nearest $ 1,000.

Output a markdown table:

| Quarter | FY 2024 Revenue | FY 2025 Revenue | YoY Growth (%) | FY 2025 vs Prev Qtr (%) |

YoY Growth (%) = growth vs same quarter last year (use bottom-chart %s).

FY 2025 vs Prev Qtr (%) = the top-chart values for FY 2025.

Leave the “Prev Qtr” cell blank for FY 2024 rows.

Rules
Extract numbers exactly as shown (currency symbol “$” optional, but include “m” or thousands separators where appropriate).

Do not invent values. If a needed number is missing, leave the cell blank.

Express all tables in valid GitHub-flavoured markdown.

Provide no explanation—only the three specified blocks.

