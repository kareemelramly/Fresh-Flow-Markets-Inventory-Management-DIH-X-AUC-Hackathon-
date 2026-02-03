import pandas as pd
import os
from pathlib import Path

data_dir = Path("data/Inventory Management")

print("=" * 80)
print("COMPREHENSIVE DATA QUALITY CHECK")
print("=" * 80)

issues = []

# Get all CSV files
csv_files = list(data_dir.glob("*.csv"))

for csv_file in sorted(csv_files):
    print(f"\n{'=' * 80}")
    print(f"FILE: {csv_file.name}")
    print(f"{'=' * 80}")
    
    try:
        df = pd.read_csv(csv_file)
        
        # Basic info
        print(f"✓ Rows: {len(df):,}")
        print(f"✓ Columns: {len(df.columns)}")
        
        # Check for completely empty file
        if len(df) == 0:
            print(f"⚠️  WARNING: File is empty (no data rows)")
            issues.append({
                'file': csv_file.name,
                'issue': 'Empty file',
                'severity': 'LOW',
                'fixable': False
            })
            continue
        
        # 1. Check for duplicate columns
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            print(f"❌ DUPLICATE COLUMNS: {duplicate_cols}")
            issues.append({
                'file': csv_file.name,
                'issue': f'Duplicate columns: {duplicate_cols}',
                'severity': 'HIGH',
                'fixable': True
            })
        
        # 2. Check for duplicate rows
        duplicates = df.duplicated()
        if duplicates.sum() > 0:
            print(f"❌ DUPLICATE ROWS: {duplicates.sum():,} ({duplicates.sum()/len(df)*100:.2f}%)")
            issues.append({
                'file': csv_file.name,
                'issue': f'{duplicates.sum()} duplicate rows',
                'severity': 'MEDIUM',
                'fixable': True
            })
        
        # 3. Check for missing values
        missing = df.isnull().sum()
        missing_cols = missing[missing > 0]
        if len(missing_cols) > 0:
            print(f"⚠️  MISSING VALUES:")
            for col, count in missing_cols.items():
                pct = count / len(df) * 100
                print(f"   - {col}: {count:,} ({pct:.2f}%)")
                if pct > 50:
                    issues.append({
                        'file': csv_file.name,
                        'issue': f'{col} has {pct:.1f}% missing values',
                        'severity': 'HIGH',
                        'fixable': False
                    })
                elif pct > 10:
                    issues.append({
                        'file': csv_file.name,
                        'issue': f'{col} has {pct:.1f}% missing values',
                        'severity': 'MEDIUM',
                        'fixable': True
                    })
        
        # 4. Check for ID column issues
        if 'id' in df.columns:
            # Check for null IDs
            null_ids = df['id'].isnull().sum()
            if null_ids > 0:
                print(f"❌ NULL IDs: {null_ids}")
                issues.append({
                    'file': csv_file.name,
                    'issue': f'{null_ids} null IDs',
                    'severity': 'HIGH',
                    'fixable': False
                })
            
            # Check for duplicate IDs
            dup_ids = df['id'].duplicated().sum()
            if dup_ids > 0:
                print(f"❌ DUPLICATE IDs: {dup_ids}")
                issues.append({
                    'file': csv_file.name,
                    'issue': f'{dup_ids} duplicate IDs',
                    'severity': 'HIGH',
                    'fixable': True
                })
        
        # 5. Check for whitespace issues
        for col in df.select_dtypes(include=['object']).columns:
            # Check for leading/trailing whitespace
            has_whitespace = df[col].astype(str).str.strip() != df[col].astype(str)
            if has_whitespace.sum() > 0:
                print(f"⚠️  WHITESPACE in {col}: {has_whitespace.sum()} values")
                issues.append({
                    'file': csv_file.name,
                    'issue': f'{col} has {has_whitespace.sum()} values with whitespace',
                    'severity': 'LOW',
                    'fixable': True
                })
        
        # 6. Check for data type inconsistencies in ID columns
        id_columns = [col for col in df.columns if col.endswith('_id') or col == 'id']
        for col in id_columns:
            if col in df.columns:
                # Check if all non-null values are numeric
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    try:
                        pd.to_numeric(non_null, errors='raise')
                    except:
                        print(f"⚠️  NON-NUMERIC IDs in {col}")
                        issues.append({
                            'file': csv_file.name,
                            'issue': f'{col} contains non-numeric values',
                            'severity': 'MEDIUM',
                            'fixable': False
                        })
        
        # 7. Check for negative values in quantity/price columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if any(keyword in col.lower() for keyword in ['quantity', 'price', 'amount', 'total', 'count']):
                negatives = (df[col] < 0).sum()
                if negatives > 0:
                    print(f"⚠️  NEGATIVE VALUES in {col}: {negatives}")
                    issues.append({
                        'file': csv_file.name,
                        'issue': f'{col} has {negatives} negative values',
                        'severity': 'MEDIUM',
                        'fixable': False
                    })
        
        # 8. Check date columns
        date_cols = [col for col in df.columns if any(word in col.lower() for word in ['date', 'created', 'updated', 'time'])]
        for col in date_cols:
            try:
                dates = pd.to_datetime(df[col], errors='coerce')
                invalid_dates = dates.isnull() & df[col].notnull()
                if invalid_dates.sum() > 0:
                    print(f"⚠️  INVALID DATES in {col}: {invalid_dates.sum()}")
                    issues.append({
                        'file': csv_file.name,
                        'issue': f'{col} has {invalid_dates.sum()} invalid dates',
                        'severity': 'MEDIUM',
                        'fixable': False
                    })
            except:
                pass
        
        if not duplicate_cols and duplicates.sum() == 0 and len(missing_cols) == 0:
            print("✅ No critical issues found")
    
    except Exception as e:
        print(f"❌ ERROR reading file: {e}")
        issues.append({
            'file': csv_file.name,
            'issue': f'Error reading file: {e}',
            'severity': 'CRITICAL',
            'fixable': False
        })

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if issues:
    print(f"\nTotal issues found: {len(issues)}\n")
    
    # Group by severity
    critical = [i for i in issues if i['severity'] == 'CRITICAL']
    high = [i for i in issues if i['severity'] == 'HIGH']
    medium = [i for i in issues if i['severity'] == 'MEDIUM']
    low = [i for i in issues if i['severity'] == 'LOW']
    
    fixable = [i for i in issues if i['fixable']]
    
    if critical:
        print(f"🔴 CRITICAL: {len(critical)}")
        for issue in critical:
            print(f"   - {issue['file']}: {issue['issue']}")
    
    if high:
        print(f"\n🟠 HIGH: {len(high)}")
        for issue in high:
            print(f"   - {issue['file']}: {issue['issue']}")
    
    if medium:
        print(f"\n🟡 MEDIUM: {len(medium)}")
        for issue in medium:
            print(f"   - {issue['file']}: {issue['issue']}")
    
    if low:
        print(f"\n🟢 LOW: {len(low)}")
        for issue in low:
            print(f"   - {issue['file']}: {issue['issue']}")
    
    print(f"\n📝 FIXABLE ISSUES: {len(fixable)}/{len(issues)}")
    if fixable:
        print("\nThe following issues can be automatically fixed:")
        for issue in fixable:
            print(f"   ✓ {issue['file']}: {issue['issue']}")
else:
    print("\n✅ NO ISSUES FOUND - All files are clean!")
