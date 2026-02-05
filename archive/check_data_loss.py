import pandas as pd
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Define paths
cleaned_path = Path("data/Inventory Management")
uncleaned_path = Path("data/Uncleaned Inventory Management data")

# Get list of all CSV files
uncleaned_files = sorted([f for f in os.listdir(uncleaned_path) if f.endswith('.csv')])
cleaned_files = sorted([f for f in os.listdir(cleaned_path) if f.endswith('.csv')])

# Open output file
output_file = open("data_loss_report.txt", "w", encoding="utf-8")

def p(text=""):
    """Print to both console and file"""
    print(text)
    output_file.write(text + "\n")

p("=" * 100)
p("DATA LOSS ANALYSIS: Cleaned vs Uncleaned Data")
p("=" * 100)
p()

# Track missing files
missing_in_cleaned = set(uncleaned_files) - set(cleaned_files)
if missing_in_cleaned:
    p("⚠️  FILES MISSING IN CLEANED DATA:")
    for file in missing_in_cleaned:
        uncleaned_file_path = uncleaned_path / file
        df = pd.read_csv(uncleaned_file_path)
        p(f"   - {file}: {len(df)} rows LOST")
    p()

# Compare row counts for common files
p("ROW COUNT COMPARISON:")
p("-" * 100)
p(f"{'File Name':<35} {'Uncleaned Rows':<18} {'Cleaned Rows':<18} {'Difference':<15} {'% Loss':<10}")
p("-" * 100)

total_uncleaned = 0
total_cleaned = 0
significant_losses = []

for file in sorted(set(uncleaned_files) & set(cleaned_files)):
    uncleaned_file_path = uncleaned_path / file
    cleaned_file_path = cleaned_path / file
    
    try:
        df_uncleaned = pd.read_csv(uncleaned_file_path)
        df_cleaned = pd.read_csv(cleaned_file_path)
        
        rows_uncleaned = len(df_uncleaned)
        rows_cleaned = len(df_cleaned)
        difference = rows_uncleaned - rows_cleaned
        
        total_uncleaned += rows_uncleaned
        total_cleaned += rows_cleaned
        
        # Calculate percentage loss
        if rows_uncleaned > 0:
            pct_loss = (difference / rows_uncleaned) * 100
        else:
            pct_loss = 0
        
        # Flag significant losses (>5%)
        flag = ""
        if pct_loss > 5:
            flag = "⚠️"
            significant_losses.append({
                'file': file,
                'uncleaned': rows_uncleaned,
                'cleaned': rows_cleaned,
                'lost': difference,
                'pct': pct_loss
            })
        elif pct_loss < 0:
            flag = "📈"  # More rows in cleaned (unusual)
        
        p(f"{file:<35} {rows_uncleaned:<18,} {rows_cleaned:<18,} {difference:<15,} {pct_loss:>8.2f}% {flag}")
        
    except Exception as e:
        p(f"{file:<35} ERROR: {str(e)}")

p("-" * 100)
overall_loss = total_uncleaned - total_cleaned
overall_pct = (overall_loss / total_uncleaned * 100) if total_uncleaned > 0 else 0
p(f"{'TOTAL':<35} {total_uncleaned:<18,} {total_cleaned:<18,} {overall_loss:<15,} {overall_pct:>8.2f}%")
p("=" * 100)
p()

# Summary
if significant_losses:
    p("⚠️  SIGNIFICANT DATA LOSSES (>5%):")
    p("-" * 100)
    for loss in significant_losses:
        p(f"   {loss['file']}: Lost {loss['lost']:,} rows ({loss['pct']:.2f}%)")
    p()

if missing_in_cleaned:
    p(f"⚠️  CRITICAL: {len(missing_in_cleaned)} file(s) completely removed from cleaned data")
    p()

if overall_pct > 10:
    p(f"⚠️  WARNING: Overall data loss is {overall_pct:.2f}% - this is substantial!")
elif overall_pct > 5:
    p(f"⚠️  CAUTION: Overall data loss is {overall_pct:.2f}% - review cleaning process")
else:
    p(f"✓ Overall data loss is {overall_pct:.2f}% - within acceptable range")

p()
p("=" * 100)
output_file.close()
