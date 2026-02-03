"""Quick fix for remaining duplicate column files"""
import os
import shutil

def fix_duplicate_columns(filepath):
    """Fix files with duplicate created/updated columns"""
    print(f"Fixing {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    if len(lines) < 2:
        print(f"  Skipped - no data")
        return
    
    header = lines[0].strip().split(',')
    
    # Find duplicate indices
    seen = {}
    clean_indices = []
    
    for i, col in enumerate(header):
        if col not in seen:
            seen[col] = i
            clean_indices.append(i)
    
    clean_header = [header[i] for i in clean_indices]
    
    # Write cleaned file
    temp_file = filepath + '.tmp'
    with open(temp_file, 'w', encoding='utf-8', newline='') as out:
        out.write(','.join(clean_header) + '\n')
        
        for line in lines[1:]:
            values = line.strip().split(',')
            clean_values = [values[i] if i < len(values) else '' for i in clean_indices]
            out.write(','.join(clean_values) + '\n')
    
    os.replace(temp_file, filepath)
    print(f"  ✅ Fixed - {len(header) - len(clean_header)} duplicates removed")

# Fix the two remaining files
data_dir = "data/Inventory Management"

files_to_fix = ['dim_add_ons.csv', 'dim_campaigns.csv']

for filename in files_to_fix:
    filepath = os.path.join(data_dir, filename)
    if os.path.exists(filepath):
        fix_duplicate_columns(filepath)

print("\n✅ All files fixed!")
