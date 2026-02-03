"""
Check for data loss across commits
Compares current files with original first commit
"""

import subprocess
import os

data_dir = "data/Inventory Management"

print("=" * 80)
print("DATA LOSS DETECTION - Comparing with First Commit")
print("=" * 80)

# Get list of CSV files
csv_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.csv')])

print(f"\nChecking {len(csv_files)} CSV files...\n")

data_lost_files = []
data_gained_files = []
unchanged_files = []

for filename in csv_files:
    filepath = f"data/Inventory Management/{filename}"
    
    # Get current line count
    try:
        with open(os.path.join(data_dir, filename), 'r', encoding='utf-8', errors='ignore') as f:
            current_lines = sum(1 for _ in f)
    except:
        current_lines = 0
    
    # Get original line count from first commit
    try:
        result = subprocess.run(
            ['git', 'show', f'2c3ee02:{filepath}'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            original_lines = len(result.stdout.strip().split('\n'))
        else:
            original_lines = 0
    except:
        original_lines = 0
    
    # Calculate difference
    diff = current_lines - original_lines
    
    # Categorize
    if diff < 0:
        data_lost_files.append((filename, original_lines, current_lines, diff))
        status = "❌ DATA LOST"
    elif diff > 0:
        data_gained_files.append((filename, original_lines, current_lines, diff))
        status = "✅ DATA GAINED"
    else:
        unchanged_files.append((filename, current_lines))
        status = "✅ UNCHANGED"
    
    # Print result
    print(f"{filename:<35} | Original: {original_lines:>7} | Current: {current_lines:>7} | {status}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if data_lost_files:
    print(f"\n❌ FILES WITH DATA LOSS: {len(data_lost_files)}")
    print("-" * 80)
    for filename, orig, curr, diff in sorted(data_lost_files, key=lambda x: x[3]):
        loss_pct = abs(((curr - orig) / orig * 100)) if orig > 0 else 0
        print(f"  {filename}")
        print(f"    Original: {orig:,} lines | Current: {curr:,} lines")
        print(f"    Lost: {abs(diff):,} lines ({loss_pct:.1f}% loss)")
        print()

if data_gained_files:
    print(f"\n✅ FILES WITH ADDITIONAL DATA: {len(data_gained_files)}")
    print("-" * 80)
    for filename, orig, curr, diff in data_gained_files[:5]:
        print(f"  {filename}: +{diff:,} lines")

print(f"\n✅ UNCHANGED FILES: {len(unchanged_files)}")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)

if data_lost_files:
    print("\n⚠️  ACTION REQUIRED: Restore files from first commit (2c3ee02)")
    print("\nTo restore all lost data, run:")
    print("  git checkout 2c3ee02 -- \"data/Inventory Management/<filename>\"")
    print("\nFiles to restore:")
    for filename, orig, curr, diff in data_lost_files:
        print(f"  - {filename}")
else:
    print("\n✅ No data loss detected! All files are intact.")
