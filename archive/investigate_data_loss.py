import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Files with significant loss
significant_losses = [
    ('dim_add_ons.csv', 53.88),
    ('dim_places.csv', 42.11),
    ('fct_orders.csv', 7.04),
    ('fct_cash_balances.csv', 7.51),
    ('fct_invoice_items.csv', 6.59)
]

cleaned_path = Path("data/Inventory Management")
uncleaned_path = Path("data/Uncleaned Inventory Management data")

results = []
results.append("=" * 100)
results.append("DATA LOSS INVESTIGATION - Analyzing What Was Lost")
results.append("=" * 100)
results.append("")

restore_recommendations = []

for file, pct_loss in significant_losses:
    results.append(f"\n{'=' * 100}")
    results.append(f"FILE: {file} (Lost {pct_loss}%)")
    results.append("=" * 100)
    
    uncleaned_df = pd.read_csv(uncleaned_path / file)
    cleaned_df = pd.read_csv(cleaned_path / file)
    
    results.append(f"\nUncleaned: {len(uncleaned_df)} rows, {len(uncleaned_df.columns)} columns")
    results.append(f"Cleaned: {len(cleaned_df)} rows, {len(cleaned_df.columns)} columns")
    results.append(f"Lost: {len(uncleaned_df) - len(cleaned_df)} rows")
    
    # Check for duplicates in uncleaned
    uncleaned_duplicates = uncleaned_df.duplicated().sum()
    cleaned_duplicates = cleaned_df.duplicated().sum()
    
    results.append(f"\nDuplicate rows in uncleaned: {uncleaned_duplicates}")
    results.append(f"Duplicate rows in cleaned: {cleaned_duplicates}")
    
    # Check for null values
    uncleaned_nulls = uncleaned_df.isnull().sum().sum()
    cleaned_nulls = cleaned_df.isnull().sum().sum()
    
    results.append(f"\nTotal null values in uncleaned: {uncleaned_nulls}")
    results.append(f"Total null values in cleaned: {cleaned_nulls}")
    
    # Check if there's a primary key column (ID)
    id_cols = [col for col in uncleaned_df.columns if 'id' in col.lower() and col != 'id']
    if 'id' in uncleaned_df.columns:
        id_cols.insert(0, 'id')
    
    if id_cols:
        results.append(f"\nPotential ID columns: {', '.join(id_cols[:3])}")
        
        # Check for duplicate IDs in the first ID column
        if id_cols[0] in uncleaned_df.columns:
            uncleaned_id_dups = uncleaned_df[id_cols[0]].duplicated().sum()
            cleaned_id_dups = cleaned_df[id_cols[0]].duplicated().sum() if id_cols[0] in cleaned_df.columns else 0
            
            results.append(f"Duplicate {id_cols[0]} in uncleaned: {uncleaned_id_dups}")
            results.append(f"Duplicate {id_cols[0]} in cleaned: {cleaned_id_dups}")
    
    # Analyze rows with all nulls
    uncleaned_all_null_rows = uncleaned_df.isnull().all(axis=1).sum()
    cleaned_all_null_rows = cleaned_df.isnull().all(axis=1).sum()
    
    results.append(f"\nRows with all nulls in uncleaned: {uncleaned_all_null_rows}")
    results.append(f"Rows with all nulls in cleaned: {cleaned_all_null_rows}")
    
    # Check rows with mostly nulls (>50% null)
    uncleaned_mostly_null = (uncleaned_df.isnull().sum(axis=1) > len(uncleaned_df.columns) * 0.5).sum()
    cleaned_mostly_null = (cleaned_df.isnull().sum(axis=1) > len(cleaned_df.columns) * 0.5).sum()
    
    results.append(f"Rows with >50% nulls in uncleaned: {uncleaned_mostly_null}")
    results.append(f"Rows with >50% nulls in cleaned: {cleaned_mostly_null}")
    
    # Analyze the loss
    rows_lost = len(uncleaned_df) - len(cleaned_df)
    
    # Calculate legitimate removals
    legitimate_removals = uncleaned_duplicates + uncleaned_all_null_rows
    
    results.append(f"\n{'-' * 100}")
    results.append("ANALYSIS:")
    results.append(f"  Rows lost: {rows_lost}")
    results.append(f"  Duplicates removed: {uncleaned_duplicates}")
    results.append(f"  All-null rows removed: {uncleaned_all_null_rows}")
    results.append(f"  Legitimate removals: {legitimate_removals}")
    results.append(f"  Unexplained loss: {rows_lost - legitimate_removals}")
    
    # Make recommendation
    if rows_lost - legitimate_removals > rows_lost * 0.1:  # >10% unexplained
        results.append(f"\n[!] RECOMMENDATION: RESTORE - Significant unexplained data loss!")
        restore_recommendations.append(file)
    elif pct_loss > 40 and rows_lost > legitimate_removals:
        results.append(f"\n[!] RECOMMENDATION: REVIEW - High loss rate, needs manual review")
        restore_recommendations.append(file)
    else:
        results.append(f"\n[OK] RECOMMENDATION: KEEP AS IS - Loss appears justified (duplicates/nulls)")

results.append(f"\n\n{'=' * 100}")
results.append("SUMMARY")
results.append("=" * 100)

if restore_recommendations:
    results.append(f"\n[!] FILES RECOMMENDED FOR RESTORATION: {len(restore_recommendations)}")
    for file in restore_recommendations:
        results.append(f"   - {file}")
else:
    results.append("\n[OK] All data losses appear justified - no restoration needed")

results.append("\n" + "=" * 100)

# Save to file first
with open("data_loss_investigation.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print("[OK] Investigation complete - report saved to data_loss_investigation.txt")
print(f"Total files analyzed: {len(significant_losses)}")
print(f"Files recommended for restoration: {len(restore_recommendations)}")

if restore_recommendations:
    print("\nFiles to restore:")
    for file in restore_recommendations:
        print(f"  - {file}")
    
    # Save list for automation
    with open("files_to_restore.txt", "w") as f:
        for file in restore_recommendations:
            f.write(file + "\n")
