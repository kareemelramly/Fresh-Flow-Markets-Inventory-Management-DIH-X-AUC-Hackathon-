import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Files to restore
files_to_restore = [
    'dim_add_ons.csv',
    'dim_places.csv',
    'fct_orders.csv',
    'fct_cash_balances.csv',
    'fct_invoice_items.csv'
]

cleaned_path = Path("data/Inventory Management")
uncleaned_path = Path("data/Uncleaned Inventory Management data")
backup_path = Path("data/Backup Before Restoration")

# Create backup directory
backup_path.mkdir(exist_ok=True)

print("=" * 100)
print("DATA RESTORATION SCRIPT")
print("=" * 100)
print(f"\nBackup directory: {backup_path}")
print(f"Files to restore: {len(files_to_restore)}\n")

restoration_summary = []

for file in files_to_restore:
    print(f"\nProcessing: {file}")
    print("-" * 100)
    
    cleaned_file = cleaned_path / file
    uncleaned_file = uncleaned_path / file
    backup_file = backup_path / file
    
    # Create backup of current cleaned file
    if cleaned_file.exists():
        shutil.copy2(cleaned_file, backup_file)
        print(f"  [OK] Backed up current version to: {backup_file}")
    
    # Read both files
    df_cleaned = pd.read_csv(cleaned_file)
    df_uncleaned = pd.read_csv(uncleaned_file)
    
    rows_before = len(df_cleaned)
    rows_uncleaned = len(df_uncleaned)
    rows_lost = rows_uncleaned - rows_before
    
    print(f"  Current cleaned rows: {rows_before:,}")
    print(f"  Uncleaned rows: {rows_uncleaned:,}")
    print(f"  Rows to restore: {rows_lost:,}")
    
    # Replace with uncleaned version
    df_uncleaned.to_csv(cleaned_file, index=False)
    
    # Verify restoration
    df_restored = pd.read_csv(cleaned_file)
    rows_after = len(df_restored)
    
    if rows_after == rows_uncleaned:
        print(f"  [SUCCESS] Restored {rows_lost:,} rows")
        restoration_summary.append({
            'file': file,
            'before': rows_before,
            'after': rows_after,
            'restored': rows_lost,
            'status': 'SUCCESS'
        })
    else:
        print(f"  [ERROR] Restoration verification failed!")
        restoration_summary.append({
            'file': file,
            'before': rows_before,
            'after': rows_after,
            'restored': rows_after - rows_before,
            'status': 'ERROR'
        })

# Summary
print("\n" + "=" * 100)
print("RESTORATION SUMMARY")
print("=" * 100)
print(f"\n{'File':<30} {'Before':<15} {'After':<15} {'Restored':<15} {'Status':<10}")
print("-" * 100)

total_restored = 0
for item in restoration_summary:
    print(f"{item['file']:<30} {item['before']:<15,} {item['after']:<15,} {item['restored']:<15,} {item['status']:<10}")
    total_restored += item['restored']

print("-" * 100)
print(f"{'TOTAL':<30} {'':<15} {'':<15} {total_restored:<15,}")

successful = sum(1 for item in restoration_summary if item['status'] == 'SUCCESS')
print(f"\n[OK] Successfully restored {successful}/{len(files_to_restore)} files")
print(f"[OK] Total rows restored: {total_restored:,}")
print(f"\n[INFO] Backups saved to: {backup_path}/")
print("=" * 100)

# Save restoration log
log_file = f"restoration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(log_file, "w") as f:
    f.write(f"Data Restoration Log - {datetime.now()}\n")
    f.write("=" * 100 + "\n\n")
    for item in restoration_summary:
        f.write(f"File: {item['file']}\n")
        f.write(f"  Rows before: {item['before']:,}\n")
        f.write(f"  Rows after: {item['after']:,}\n")
        f.write(f"  Rows restored: {item['restored']:,}\n")
        f.write(f"  Status: {item['status']}\n\n")
    f.write(f"\nTotal rows restored: {total_restored:,}\n")
    f.write(f"Backup location: {backup_path}/\n")

print(f"\n[OK] Restoration log saved to: {log_file}")
