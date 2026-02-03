"""
Comprehensive Data Quality Analysis
Checks all CSV files in detail
"""

import os
import csv

data_dir = "data/Inventory Management"

print("=" * 80)
print("COMPREHENSIVE DATA QUALITY REPORT")
print("=" * 80)

files = sorted([f for f in os.listdir(data_dir) if f.endswith('.csv')])

total_files = len(files)
files_with_data = 0
total_rows = 0
issues_found = []

for filename in files:
    filepath = os.path.join(data_dir, filename)
    
    print(f"\n{'='*80}")
    print(f"📄 {filename}")
    print(f"{'='*80}")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            lines = list(reader)
        
        if len(lines) == 0:
            print("❌ EMPTY FILE")
            issues_found.append(f"{filename}: Empty file")
            continue
        
        header = lines[0]
        data_rows = lines[1:]
        
        print(f"Rows: {len(data_rows):,} (+ 1 header)")
        print(f"Columns: {len(header)}")
        
        if len(data_rows) > 0:
            files_with_data += 1
            total_rows += len(data_rows)
        
        # Check for duplicate columns
        duplicates = [col for col in set(header) if header.count(col) > 1]
        if duplicates:
            print(f"⚠️  DUPLICATE COLUMNS: {duplicates}")
            issues_found.append(f"{filename}: Duplicate columns - {duplicates}")
        
        # Check first 5 rows for data quality
        if len(data_rows) > 0:
            print(f"\nFirst row analysis:")
            first_row = data_rows[0]
            
            # Count empty values
            empty_count = sum(1 for v in first_row if not v or v.strip() == '')
            if empty_count > 0:
                empty_pct = (empty_count / len(first_row)) * 100
                print(f"  Empty values: {empty_count}/{len(first_row)} ({empty_pct:.1f}%)")
                if empty_pct > 50:
                    issues_found.append(f"{filename}: >50% empty values in first row")
            
            # Check column count consistency
            if len(first_row) != len(header):
                print(f"  ⚠️  Column mismatch: Header={len(header)}, Row={len(first_row)}")
                issues_found.append(f"{filename}: Column count mismatch")
            
            # Sample first few values
            print(f"  Sample values (first 3 columns):")
            for i, (col, val) in enumerate(zip(header[:3], first_row[:3])):
                display_val = val[:50] + "..." if len(val) > 50 else val
                print(f"    {col}: {display_val}")
        
        else:
            print("⚠️  NO DATA ROWS (header only)")
            issues_found.append(f"{filename}: No data rows")
        
        # Check last row to see if file is complete
        if len(data_rows) > 1:
            last_row = data_rows[-1]
            if all(not v or v.strip() == '' for v in last_row):
                print("  ⚠️  Last row is completely empty")
        
    except Exception as e:
        print(f"❌ ERROR reading file: {e}")
        issues_found.append(f"{filename}: Read error - {e}")

# Summary
print(f"\n{'='*80}")
print("SUMMARY STATISTICS")
print(f"{'='*80}")
print(f"\nTotal files: {total_files}")
print(f"Files with data: {files_with_data}")
print(f"Files empty (header only): {total_files - files_with_data}")
print(f"Total data rows: {total_rows:,}")

print(f"\n{'='*80}")
print("ISSUES FOUND")
print(f"{'='*80}")

if issues_found:
    print(f"\nTotal issues: {len(issues_found)}\n")
    for i, issue in enumerate(issues_found, 1):
        print(f"{i}. {issue}")
else:
    print("\n✅ No critical issues found!")

print(f"\n{'='*80}")
print("FILE SIZE DISTRIBUTION")
print(f"{'='*80}")

# Group files by size
small = []  # < 100 rows
medium = []  # 100-10,000 rows
large = []  # 10,000+ rows
empty = []  # 0 rows

for filename in files:
    filepath = os.path.join(data_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            line_count = sum(1 for _ in f) - 1  # Subtract header
        
        if line_count == 0:
            empty.append(filename)
        elif line_count < 100:
            small.append((filename, line_count))
        elif line_count < 10000:
            medium.append((filename, line_count))
        else:
            large.append((filename, line_count))
    except:
        pass

print(f"\n📊 Empty (0 rows): {len(empty)}")
for f in empty:
    print(f"   - {f}")

print(f"\n📊 Small (<100 rows): {len(small)}")
for f, count in sorted(small, key=lambda x: x[1], reverse=True):
    print(f"   - {f}: {count:,} rows")

print(f"\n📊 Medium (100-10K rows): {len(medium)}")
for f, count in sorted(medium, key=lambda x: x[1], reverse=True)[:5]:
    print(f"   - {f}: {count:,} rows")
if len(medium) > 5:
    print(f"   ... and {len(medium)-5} more")

print(f"\n📊 Large (10K+ rows): {len(large)}")
for f, count in sorted(large, key=lambda x: x[1], reverse=True):
    print(f"   - {f}: {count:,} rows")

print(f"\n{'='*80}")
print("DATA READY FOR DATABASE: {'✅ YES' if len(issues_found) < 5 else '⚠️  WITH WARNINGS'}")
print(f"{'='*80}\n")
