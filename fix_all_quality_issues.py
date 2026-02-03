import pandas as pd
import os
from pathlib import Path
import sys

# Force UTF-8 encoding for output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

data_dir = Path("data/Inventory Management")
backup_dir = Path("data/Inventory Management - Quality Backup")
backup_dir.mkdir(exist_ok=True)

print("=" * 80)
print("DATA QUALITY CHECK & FIX")
print("=" * 80)

issues_found = []
issues_fixed = []

# Get all CSV files
csv_files = sorted(data_dir.glob("*.csv"))

for csv_file in csv_files:
    print(f"\n[{csv_file.name}]")
    
    try:
        # Try to read with default settings first
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            # If parsing error, try with more lenient settings
            print(f"  CRITICAL: Parsing error - {str(e)[:100]}")
            print(f"  Attempting to fix with lenient parsing...")
            try:
                df = pd.read_csv(csv_file, on_bad_lines='skip', engine='python')
                issues_found.append(f"{csv_file.name}: Malformed CSV rows (skipped bad lines)")
                issues_fixed.append(f"{csv_file.name}: Fixed malformed CSV")
                # Save backup
                import shutil
                shutil.copy2(csv_file, backup_dir / csv_file.name)
                # Save fixed version
                df.to_csv(csv_file, index=False)
                print(f"  FIXED: Saved cleaned version (backup in: {backup_dir})")
            except Exception as e2:
                print(f"  ERROR: Could not fix - {e2}")
                issues_found.append(f"{csv_file.name}: UNFIXABLE - {str(e2)[:100]}")
                continue
        
        if len(df) == 0:
            print(f"  WARNING: Empty file (only header)")
            continue
            
        print(f"  Rows: {len(df):,} | Columns: {len(df.columns)}")
        
        fixed_this_file = False
        
        # 1. Remove duplicate columns
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            print(f"  ISSUE: Duplicate columns: {duplicate_cols}")
            issues_found.append(f"{csv_file.name}: Duplicate columns {duplicate_cols}")
            
            # Keep only first occurrence of each column
            df = df.loc[:, ~df.columns.duplicated()]
            fixed_this_file = True
            issues_fixed.append(f"{csv_file.name}: Removed duplicate columns")
            print(f"  FIXED: Removed duplicate columns")
        
        # 2. Remove duplicate rows
        duplicates = df.duplicated()
        if duplicates.sum() > 0:
            print(f"  ISSUE: {duplicates.sum():,} duplicate rows ({duplicates.sum()/len(df)*100:.1f}%)")
            issues_found.append(f"{csv_file.name}: {duplicates.sum()} duplicate rows")
            
            df = df.drop_duplicates()
            fixed_this_file = True
            issues_fixed.append(f"{csv_file.name}: Removed {duplicates.sum()} duplicate rows")
            print(f"  FIXED: Removed duplicate rows")
        
        # 3. Remove duplicate IDs
        if 'id' in df.columns:
            dup_ids = df['id'].duplicated()
            if dup_ids.sum() > 0:
                print(f"  ISSUE: {dup_ids.sum()} duplicate IDs")
                issues_found.append(f"{csv_file.name}: {dup_ids.sum()} duplicate IDs")
                
                # Keep first occurrence of each ID
                df = df.drop_duplicates(subset=['id'], keep='first')
                fixed_this_file = True
                issues_fixed.append(f"{csv_file.name}: Removed duplicate IDs")
                print(f"  FIXED: Removed duplicate IDs")
        
        # 4. Strip whitespace from string columns
        whitespace_fixed = 0
        for col in df.select_dtypes(include=['object']).columns:
            original = df[col].astype(str)
            stripped = original.str.strip()
            changes = (original != stripped).sum()
            if changes > 0:
                df[col] = df[col].str.strip()
                whitespace_fixed += changes
        
        if whitespace_fixed > 0:
            print(f"  FIXED: Trimmed whitespace from {whitespace_fixed} values")
            fixed_this_file = True
            issues_fixed.append(f"{csv_file.name}: Trimmed {whitespace_fixed} whitespace values")
        
        # 5. Report missing values (but don't fix - may be intentional)
        missing = df.isnull().sum()
        missing_cols = missing[missing > 0]
        if len(missing_cols) > 0:
            high_missing = missing_cols[missing_cols / len(df) > 0.5]
            if len(high_missing) > 0:
                print(f"  WARNING: High missing values:")
                for col, count in high_missing.items():
                    print(f"    - {col}: {count:,} ({count/len(df)*100:.1f}%)")
        
        # Save if any fixes were made
        if fixed_this_file:
            # Create backup first
            import shutil
            shutil.copy2(csv_file, backup_dir / csv_file.name)
            
            # Save cleaned version
            df.to_csv(csv_file, index=False)
            print(f"  SAVED: Updated file")
        else:
            print(f"  OK: No issues found")
    
    except Exception as e:
        print(f"  ERROR: {e}")
        issues_found.append(f"{csv_file.name}: ERROR - {str(e)[:100]}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if issues_found:
    print(f"\nTotal issues found: {len(issues_found)}")
    for issue in issues_found:
        print(f"  - {issue}")

if issues_fixed:
    print(f"\n\nTotal fixes applied: {len(issues_fixed)}")
    for fix in issues_fixed:
        print(f"  ✓ {fix}")
    print(f"\nBackups saved to: {backup_dir}")
else:
    print("\n✅ All files are clean - no fixes needed!")
