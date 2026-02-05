import shutil
from pathlib import Path
from datetime import datetime
import os

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
print("DATA RESTORATION SCRIPT - Using File Copy Method")
print("=" * 100)
print(f"\nBackup directory: {backup_path}")
print(f"Files to restore: {len(files_to_restore)}")
print("\nNOTE: Please close any open CSV files in editors before proceeding.")
print("=" * 100)

restoration_summary = []
total_errors = 0

for file in files_to_restore:
    print(f"\n[{files_to_restore.index(file) + 1}/{len(files_to_restore)}] Processing: {file}")
    print("-" * 100)
    
    cleaned_file = cleaned_path / file
    uncleaned_file = uncleaned_path / file
    backup_file = backup_path / file
    
    try:
        # Get file sizes before
        cleaned_size = os.path.getsize(cleaned_file)
        uncleaned_size = os.path.getsize(uncleaned_file)
        
        # Create backup of current cleaned file
        if cleaned_file.exists():
            shutil.copy2(cleaned_file, backup_file)
            print(f"  [√] Backed up current version ({cleaned_size:,} bytes)")
        
        # Replace with uncleaned version using copy2
        shutil.copy2(uncleaned_file, cleaned_file)
        
        # Verify restoration
        restored_size = os.path.getsize(cleaned_file)
        
        if restored_size == uncleaned_size:
            size_increase = uncleaned_size - cleaned_size
            print(f"  [√] Restored successfully ({uncleaned_size:,} bytes, +{size_increase:,} bytes)")
            restoration_summary.append({
                'file': file,
                'status': 'SUCCESS',
                'size_before': cleaned_size,
                'size_after': restored_size
            })
        else:
            print(f"  [X] Verification failed - size mismatch!")
            restoration_summary.append({
                'file': file,
                'status': 'VERIFY_FAILED',
                'size_before': cleaned_size,
                'size_after': restored_size
            })
            total_errors += 1
            
    except PermissionError:
        print(f"  [X] ERROR: File is open in an editor. Please close it and try again.")
        restoration_summary.append({
            'file': file,
            'status': 'PERMISSION_ERROR',
            'size_before': 0,
            'size_after': 0
        })
        total_errors += 1
    except Exception as e:
        print(f"  [X] ERROR: {str(e)}")
        restoration_summary.append({
            'file': file,
            'status': f'ERROR: {str(e)}',
            'size_before': 0,
            'size_after': 0
        })
        total_errors += 1

# Summary
print("\n" + "=" * 100)
print("RESTORATION SUMMARY")
print("=" * 100)
print(f"\n{'File':<35} {'Status':<20} {'Size Before':<15} {'Size After':<15}")
print("-" * 100)

for item in restoration_summary:
    status_symbol = "[√]" if item['status'] == 'SUCCESS' else "[X]"
    print(f"{item['file']:<35} {status_symbol} {item['status']:<18} {item['size_before']:<15,} {item['size_after']:<15,}")

successful = sum(1 for item in restoration_summary if item['status'] == 'SUCCESS')
print("-" * 100)
print(f"\nSuccessfully restored: {successful}/{len(files_to_restore)} files")
print(f"Errors encountered: {total_errors}")
print(f"\nBackups saved to: {backup_path}/")
print("=" * 100)

# Save restoration log
log_file = f"restoration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(log_file, "w") as f:
    f.write(f"Data Restoration Log - {datetime.now()}\n")
    f.write("=" * 100 + "\n\n")
    for item in restoration_summary:
        f.write(f"File: {item['file']}\n")
        f.write(f"  Status: {item['status']}\n")
        f.write(f"  Size before: {item['size_before']:,} bytes\n")
        f.write(f"  Size after: {item['size_after']:,} bytes\n\n")
    f.write(f"\nSuccessfully restored: {successful}/{len(files_to_restore)} files\n")
    f.write(f"Backup location: {backup_path}/\n")

print(f"\nRestoration log saved to: {log_file}")

if total_errors > 0:
    print("\n[!] Some files could not be restored. Please close all CSV files and run this script again.")
else:
    print("\n[√] All files restored successfully!")
