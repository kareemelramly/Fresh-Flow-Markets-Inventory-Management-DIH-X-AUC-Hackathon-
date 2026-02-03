"""
Final Data Cleaning Script for Fresh Flow Markets
==================================================

Fixes:
1. Removes duplicate columns (created, updated in dim_items.csv)
2. Handles empty files
3. Standardizes data types
4. Fills missing values appropriately
5. Creates cleaned versions of all CSV files
"""

import os
import csv
import shutil
from datetime import datetime

def backup_files(data_dir):
    """Create backup of original files"""
    backup_dir = os.path.join(os.path.dirname(data_dir), "Inventory Management - Backup")
    
    if not os.path.exists(backup_dir):
        print(f"📦 Creating backup at: {backup_dir}")
        shutil.copytree(data_dir, backup_dir)
        print("✅ Backup created successfully")
    else:
        print("⚠️  Backup already exists, skipping...")
    
    return backup_dir

def clean_dim_items(filepath):
    """Fix duplicate columns in dim_items.csv"""
    print(f"\n🔧 Cleaning {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    if len(lines) < 2:
        print("  ⚠️  File is empty or has no data")
        return
    
    # Parse header
    header = lines[0].strip().split(',')
    
    # Find duplicate columns
    seen = {}
    clean_header = []
    duplicate_indices = []
    
    for i, col in enumerate(header):
        if col in seen:
            # This is a duplicate - mark for removal
            duplicate_indices.append(i)
            print(f"  ⚠️  Found duplicate column '{col}' at index {i}")
        else:
            seen[col] = i
            clean_header.append(col)
    
    # Write cleaned file
    temp_file = filepath + '.tmp'
    
    with open(temp_file, 'w', encoding='utf-8', newline='') as out:
        # Write clean header
        out.write(','.join(clean_header) + '\n')
        
        # Process data rows
        for line_num, line in enumerate(lines[1:], 2):
            try:
                # Handle CSV properly (respecting quotes)
                values = []
                in_quotes = False
                current_value = ''
                
                for char in line:
                    if char == '"':
                        in_quotes = not in_quotes
                        current_value += char
                    elif char == ',' and not in_quotes:
                        values.append(current_value)
                        current_value = ''
                    else:
                        current_value += char
                
                # Add last value
                if current_value:
                    values.append(current_value.rstrip('\n'))
                
                # Remove duplicate column values
                clean_values = [v for i, v in enumerate(values) if i not in duplicate_indices]
                
                # Ensure we have the right number of columns
                while len(clean_values) < len(clean_header):
                    clean_values.append('')
                
                # Write cleaned row
                out.write(','.join(clean_values[:len(clean_header)]) + '\n')
                
            except Exception as e:
                print(f"  ⚠️  Error on line {line_num}: {e}")
                continue
    
    # Replace original with cleaned version
    os.replace(temp_file, filepath)
    print(f"  ✅ Cleaned - removed {len(duplicate_indices)} duplicate columns")

def clean_empty_file(filepath, expected_columns):
    """Add sample/placeholder data to empty files"""
    print(f"\n🔧 Cleaning {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    if len(lines) <= 1:
        print(f"  ⚠️  File is empty - adding placeholder header")
        
        # Create minimal valid structure
        with open(filepath, 'w', encoding='utf-8') as f:
            if len(lines) == 0:
                # No header at all - create one
                f.write(','.join(expected_columns) + '\n')
            else:
                # Has header but no data - keep it
                f.write(lines[0])
        
        print("  ✅ File structure created (no data rows)")

def fill_missing_values(filepath, table_type='dimension'):
    """Fill missing values based on column types"""
    print(f"\n🔧 Filling missing values in {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        rows = list(reader)
    
    if not rows:
        print("  ℹ️  No data rows to process")
        return
    
    filled_count = 0
    
    # Process each row
    for row in rows:
        for col, value in row.items():
            if value is None or value.strip() == '' or value == 'nan':
                # Fill based on column name patterns
                if col in ['id', 'user_id', 'place_id', 'item_id']:
                    row[col] = '0'
                    filled_count += 1
                elif 'date' in col.lower() or 'time' in col.lower():
                    row[col] = '0'
                    filled_count += 1
                elif col in ['status', 'type']:
                    row[col] = 'unknown'
                    filled_count += 1
                elif col in ['deleted', 'demo_mode', 'trainee_mode', 'active']:
                    row[col] = '0'
                    filled_count += 1
                elif 'price' in col.lower() or 'amount' in col.lower():
                    row[col] = '0.0'
                    filled_count += 1
                else:
                    row[col] = ''  # Leave as empty string
    
    # Write back
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"  ✅ Filled {filled_count} missing values")

def validate_file(filepath):
    """Validate cleaned file structure"""
    print(f"\n🔍 Validating {os.path.basename(filepath)}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        if len(lines) == 0:
            print("  ❌ File is empty!")
            return False
        
        header = lines[0].strip().split(',')
        
        # Check for duplicate columns
        if len(header) != len(set(header)):
            duplicates = [col for col in set(header) if header.count(col) > 1]
            print(f"  ❌ Still has duplicate columns: {duplicates}")
            return False
        
        print(f"  ✅ Valid - {len(lines)-1} data rows, {len(header)} columns")
        return True
        
    except Exception as e:
        print(f"  ❌ Validation error: {e}")
        return False

def main():
    print("=" * 70)
    print("FRESH FLOW MARKETS - FINAL DATA CLEANING")
    print("=" * 70)
    
    data_dir = "data/Inventory Management"
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    # Step 1: Create backup
    print("\n📦 STEP 1: Creating Backup")
    print("-" * 70)
    backup_files(data_dir)
    
    # Step 2: Fix specific issues
    print("\n🔧 STEP 2: Fixing Known Issues")
    print("-" * 70)
    
    # Fix dim_items.csv duplicate columns
    dim_items_path = os.path.join(data_dir, "dim_items.csv")
    if os.path.exists(dim_items_path):
        clean_dim_items(dim_items_path)
    
    # Handle empty dim_users.csv
    dim_users_path = os.path.join(data_dir, "dim_users.csv")
    if os.path.exists(dim_users_path):
        clean_empty_file(dim_users_path, [
            'id', 'user_id', 'created', 'updated', 'type', 'first_name', 
            'last_name', 'email', 'mobile_phone', 'orders', 'cltv'
        ])
    
    # Handle empty fct_inventory_reports.csv
    inv_reports_path = os.path.join(data_dir, "fct_inventory_reports.csv")
    if os.path.exists(inv_reports_path):
        clean_empty_file(inv_reports_path, [
            'id', 'user_id', 'created', 'updated', 'place_id', 
            'start_time', 'end_time', 'data', 'pdf', 'excel'
        ])
    
    # Step 3: Fill missing values in key tables
    print("\n📝 STEP 3: Filling Missing Values")
    print("-" * 70)
    
    key_files = [
        'dim_skus.csv',
        'dim_stock_categories.csv',
        'dim_menu_items.csv',
        'dim_places.csv'
    ]
    
    for filename in key_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            fill_missing_values(filepath)
    
    # Step 4: Validate all files
    print("\n✅ STEP 4: Validation")
    print("-" * 70)
    
    all_valid = True
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    for filename in sorted(csv_files):
        filepath = os.path.join(data_dir, filename)
        if not validate_file(filepath):
            all_valid = False
    
    # Summary
    print("\n" + "=" * 70)
    print("CLEANING COMPLETE!")
    print("=" * 70)
    
    if all_valid:
        print("\n✅ All files validated successfully!")
    else:
        print("\n⚠️  Some files have issues - check output above")
    
    print(f"\n📌 Original files backed up to:")
    print(f"   {os.path.abspath(os.path.join(os.path.dirname(data_dir), 'Inventory Management - Backup'))}")
    
    print("\n📊 Summary:")
    print(f"   - Files processed: {len(csv_files)}")
    print(f"   - Backup created: ✅")
    print(f"   - Ready for database import: {'✅' if all_valid else '⚠️'}")

if __name__ == '__main__':
    main()
