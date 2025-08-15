import pandas as pd
from pathlib import Path

def analyze_leads_file(file_path, file_name):
    """Analyze a leads file and return key information."""
    print(f"\n{'='*60}")
    print(f"ANALYSIS OF {file_name}")
    print(f"{'='*60}")
    
    try:
        df = pd.read_excel(file_path, sheet_name='All deals')
        
        print(f"Shape: {df.shape}")
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        
        print(f"\nColumns:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1:2d}. {col}")
        
        print(f"\nColumn data types:")
        for col in df.columns:
            dtype = df[col].dtype
            non_null_count = df[col].count()
            null_count = df[col].isnull().sum()
            print(f"  {col}: {dtype} (non-null: {non_null_count}, null: {null_count})")
        
        # Check for key columns that SalesLeadAnalyzer depends on
        key_columns = ['Deal Name', 'Deal owner', 'Amount', 'Sale Conviction', 'Engagement Type']
        print(f"\nKey columns check:")
        for col in key_columns:
            if col in df.columns:
                unique_values = df[col].dropna().unique()
                print(f"  ✓ {col}: {len(unique_values)} unique values")
                if len(unique_values) <= 10:
                    print(f"    Values: {list(unique_values)}")
            else:
                print(f"  ✗ {col}: MISSING")
        
        # Check for deal owners specifically
        if 'Deal owner' in df.columns:
            deal_owners = df['Deal owner'].dropna().unique()
            print(f"\nDeal owners found:")
            for owner in sorted(deal_owners):
                count = len(df[df['Deal owner'] == owner])
                print(f"  {owner}: {count} deals")
        
        return df
        
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
        return None

def analyze_business_logic_implications(original_df, new_df):
    """Analyze the implications for SalesLeadAnalyzer business logic."""
    print(f"\n{'='*60}")
    print("BUSINESS LOGIC IMPLICATIONS FOR SALESLEADANALYZER")
    print(f"{'='*60}")
    
    # Industry owners from SalesLeadAnalyzer
    industry_owners = ["Hamish Bignell", "Paul Tardio", "Beth Reeve", "Katie King"]
    
    print(f"\n1. INDUSTRY OWNERS ANALYSIS:")
    print(f"   Industry owners defined in code: {industry_owners}")
    
    # Check original file
    if original_df is not None:
        original_industry_deals = original_df[original_df['Deal owner'].isin(industry_owners)]
        original_government_deals = original_df[~original_df['Deal owner'].isin(industry_owners)]
        print(f"   Original file:")
        print(f"     Industry deals: {len(original_industry_deals)}")
        print(f"     Government deals: {len(original_government_deals)}")
        print(f"     Total: {len(original_df)}")
    
    # Check new file
    if new_df is not None:
        new_industry_deals = new_df[new_df['Deal owner'].isin(industry_owners)]
        new_government_deals = new_df[~new_df['Deal owner'].isin(industry_owners)]
        print(f"   New file:")
        print(f"     Industry deals: {len(new_industry_deals)}")
        print(f"     Government deals: {len(new_government_deals)}")
        print(f"     Total: {len(new_df)}")
        
        # Check for missing deal owners
        new_owners = set(new_df['Deal owner'].dropna().unique())
        missing_owners = set(industry_owners) - new_owners
        if missing_owners:
            print(f"     WARNING: Missing industry owners in new file: {missing_owners}")
    
    print(f"\n2. ENGAGEMENT TYPE ANALYSIS:")
    if original_df is not None:
        original_engagement_types = original_df['Engagement Type'].value_counts()
        print(f"   Original file engagement types:")
        for eng_type, count in original_engagement_types.items():
            print(f"     {eng_type}: {count}")
    
    if new_df is not None:
        new_engagement_types = new_df['Engagement Type'].value_counts()
        print(f"   New file engagement types:")
        for eng_type, count in new_engagement_types.items():
            print(f"     {eng_type}: {count}")
    
    print(f"\n3. SALE CONVICTION ANALYSIS:")
    if original_df is not None:
        original_convictions = original_df['Sale Conviction'].value_counts()
        print(f"   Original file convictions:")
        for conviction, count in original_convictions.items():
            print(f"     {conviction}: {count}")
    
    if new_df is not None:
        new_convictions = new_df['Sale Conviction'].value_counts()
        print(f"   New file convictions:")
        for conviction, count in new_convictions.items():
            print(f"     {conviction}: {count}")
    
    print(f"\n4. AMOUNT ANALYSIS:")
    if original_df is not None:
        print(f"   Original file amount stats:")
        print(f"     Min: ${original_df['Amount'].min():,}")
        print(f"     Max: ${original_df['Amount'].max():,}")
        print(f"     Mean: ${original_df['Amount'].mean():,.0f}")
        print(f"     Total: ${original_df['Amount'].sum():,}")
    
    if new_df is not None:
        print(f"   New file amount stats:")
        print(f"     Min: ${new_df['Amount'].min():,}")
        print(f"     Max: ${new_df['Amount'].max():,}")
        print(f"     Mean: ${new_df['Amount'].mean():,.0f}")
        print(f"     Total: ${new_df['Amount'].sum():,}")
    
    print(f"\n5. POTENTIAL ISSUES:")
    
    # Check for null deal owners in new file
    if new_df is not None:
        null_owners = new_df[new_df['Deal owner'].isnull()]
        if len(null_owners) > 0:
            print(f"   ⚠️  New file has {len(null_owners)} rows with null Deal owner")
            print(f"      This will cause issues with sector calculation")
    
    # Check for missing key columns
    key_columns = ['Deal Name', 'Deal owner', 'Amount', 'Sale Conviction', 'Engagement Type']
    missing_in_new = [col for col in key_columns if col not in new_df.columns]
    if missing_in_new:
        print(f"   ❌ Missing key columns in new file: {missing_in_new}")
    else:
        print(f"   ✅ All key columns present in new file")
    
    # Check for data type changes
    if original_df is not None and new_df is not None:
        for col in key_columns:
            if col in original_df.columns and col in new_df.columns:
                orig_dtype = original_df[col].dtype
                new_dtype = new_df[col].dtype
                if orig_dtype != new_dtype:
                    print(f"   ⚠️  Data type change for {col}: {orig_dtype} → {new_dtype}")

def main():
    # Analyze both files
    original_df = analyze_leads_file("data/raw/Leads.xlsx", "ORIGINAL LEADS.XLSX")
    new_df = analyze_leads_file("data/raw/Leads v2.xlsx", "NEW LEADS V2.XLSX")
    
    if original_df is not None and new_df is not None:
        print(f"\n{'='*60}")
        print("COMPARISON SUMMARY")
        print(f"{'='*60}")
        
        # Compare shapes
        print(f"Row count: {len(original_df)} → {len(new_df)} ({len(new_df) - len(original_df):+d})")
        print(f"Column count: {len(original_df.columns)} → {len(new_df.columns)} ({len(new_df.columns) - len(original_df.columns):+d})")
        
        # Compare columns
        original_cols = set(original_df.columns)
        new_cols = set(new_df.columns)
        
        removed_cols = original_cols - new_cols
        added_cols = new_cols - original_cols
        common_cols = original_cols & new_cols
        
        print(f"\nRemoved columns ({len(removed_cols)}):")
        for col in sorted(removed_cols):
            print(f"  - {col}")
            
        print(f"\nAdded columns ({len(added_cols)}):")
        for col in sorted(added_cols):
            print(f"  + {col}")
            
        print(f"\nCommon columns ({len(common_cols)}):")
        for col in sorted(common_cols):
            print(f"  = {col}")
        
        # Analyze business logic implications
        analyze_business_logic_implications(original_df, new_df)

if __name__ == "__main__":
    main() 