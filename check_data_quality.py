"""
Quick Data Quality Check Script
Verifies the cleaning claims in README.md
"""

import os

# Check CSV files for basic quality issues
data_dir = "data/Inventory Management"

print("=" * 70)
print("DATA QUALITY VERIFICATION")
print("=" * 70)

files = [
    "dim_skus.csv",
    "dim_stock_categories.csv", 
    "dim_taxonomy_terms.csv",
    "dim_users.csv",
    "fct_orders.csv",
    "dim_items.csv"
]

for filename in files:
    filepath = os.path.join(data_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"\n❌ {filename}: FILE NOT FOUND")
        continue
    
    print(f"\n{'='*70}")
    print(f"📄 {filename}")
    print(f"{'='*70}")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    total_lines = len(lines)
    print(f"Total lines: {total_lines:,}")
    
    if total_lines == 0:
        print("❌ EMPTY FILE!")
        continue
    
    if total_lines == 1:
        print("⚠️  ONLY HEADER - NO DATA!")
        continue
        
    # Check header
    header = lines[0].strip()
    columns = header.split(',')
    print(f"Columns: {len(columns)}")
    
    # Check for duplicate column names
    duplicates = [col for col in set(columns) if columns.count(col) > 1]
    if duplicates:
        print(f"⚠️  DUPLICATE COLUMNS: {duplicates}")
    
    # Sample first data row
    if total_lines > 1:
        first_row = lines[1].strip()
        values = first_row.split(',')
        
        # Check for empty values in first row
        empty_count = sum(1 for v in values if v == '' or v == '""')
        if empty_count > 0:
            print(f"⚠️  Empty values in first row: {empty_count}/{len(values)}")
        
        # Check if row has expected number of columns
        if len(values) != len(columns):
            print(f"⚠️  Column mismatch: Header={len(columns)}, Row1={len(values)}")
    
    # Quick scan for completely empty rows
    empty_rows = 0
    for i, line in enumerate(lines[1:101], 1):  # Check first 100 rows
        if line.strip() == '' or line.strip() == ',':
            empty_rows += 1
    
    if empty_rows > 0:
        print(f"⚠️  Empty rows in first 100: {empty_rows}")

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print("\n📋 FILES CHECKED:")
print("   ✅ = Good structure")
print("   ⚠️  = Has issues (see above)")
print("   ❌ = Critical problem")
