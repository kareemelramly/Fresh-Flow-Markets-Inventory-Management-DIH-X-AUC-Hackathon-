# Fixed Data Cleaning Script for fct_orders.csv
# This script fixes the bugs that removed 98.6% of registered customers

import pandas as pd
import numpy as np
from scipy import stats
import os

print("="*80)
print("🔧 FIXED FCT_ORDERS CLEANING SCRIPT")
print("="*80)
print()

# Load uncleaned data
uncleaned_path = r'data\Uncleaned Inventory Management data\fct_orders.csv'
print(f"Loading: {uncleaned_path}")
df = pd.read_csv(uncleaned_path)

print(f"Original shape: {df.shape}")
print(f"Original registered orders (user_id>0): {(df['user_id'] > 0).sum():,}")
print()

# Drop unnecessary columns
print("Step 1: Dropping unnecessary columns...")
cols_to_drop = [
    'referring_user_id', 'driver_id', 'rejection_reason', 'split_bill_type', 
    'delivery_location_id', 'pickup_time', 'external_id', 'service_charge', 
    'customer_mobile_phone','customer_name', 'account_id', 'split_bill',
    'table_id', 'synchronized_to_accounting'
]
existing_cols_to_drop = [col for col in cols_to_drop if col in df.columns]
df.drop(existing_cols_to_drop, axis=1, inplace=True)
print(f"  Dropped {len(existing_cols_to_drop)} columns")
print()

# Handle missing data
print("Step 2: Handling missing data...")
# Fill updated_by with user_id when null (supposing that the user updated their own order)
df.loc[df['updated_by'].isnull(), 'updated_by'] = df.loc[df['updated_by'].isnull(), 'user_id']
df['instructions'] = df['instructions'].fillna("none")

# Drop rows with critical missing data
before_dropna = len(df)
# Only drop rows where CRITICAL fields are missing
critical_fields = ['user_id', 'place_id', 'total_amount', 'status', 'created']
df.dropna(subset=critical_fields, inplace=True)
after_dropna = len(df)
print(f"  Dropped {before_dropna - after_dropna:,} rows with missing critical fields")
print(f"  Registered orders after dropna: {(df['user_id'] > 0).sum():,}")
print()

# Convert timestamps - FIXED: Don't convert updated_by as timestamp!
print("Step 3: Converting timestamps...")
df['created'] = pd.to_datetime(df['created'], unit='s', errors='coerce')
df['updated'] = pd.to_datetime(df['updated'], unit='s', errors='coerce')
# updated_by is a user_id, NOT a timestamp - keep it as integer
df['updated_by'] = df['updated_by'].astype(int)
print("  ✅ Timestamps converted (updated_by kept as user_id)")
print()

# Remove duplicates
print("Step 4: Removing duplicates...")
before_dedup = len(df)
df.drop_duplicates(subset=['id'], inplace=True)
after_dedup = len(df)
print(f"  Removed {before_dedup - after_dedup:,} duplicate rows")
print(f"  Registered orders after dedup: {(df['user_id'] > 0).sum():,}")
print()

# FIXED: Outlier removal - EXCLUDE user_id from outlier detection!
print("Step 5: Removing outliers (FIXED - excluding user_id)...")
# user_id should NOT be checked for outliers - it's an identifier, not a metric!
cols_to_check = [col for col in df.select_dtypes(include=[np.number]).columns 
                 if not any(x in col.lower() for x in ['id', 'created', 'updated', 'user'])]

print(f"  Columns checked for outliers: {cols_to_check}")

before_outlier = len(df)
registered_before = (df['user_id'] > 0).sum()

# Use z-score but only on numerical metrics, NOT identifiers
z_scores = np.abs(stats.zscore(df[cols_to_check].fillna(0)))    
df = df[(z_scores < 3).all(axis=1)]

after_outlier = len(df)
registered_after = (df['user_id'] > 0).sum()

print(f"  Removed {before_outlier - after_outlier:,} outlier rows")
print(f"  Registered orders BEFORE outlier removal: {registered_before:,}")
print(f"  Registered orders AFTER outlier removal: {registered_after:,}")
print(f"  ✅ Retained {registered_after/registered_before*100:.1f}% of registered customer orders")
print()

# Add feature engineering
print("Step 6: Adding derived features...")
df['created_at'] = df['created']
df['order_hour'] = df['created'].dt.hour
df['order_day_of_week'] = df['created'].dt.dayofweek
df['order_month'] = df['created'].dt.month
df['order_year'] = df['created'].dt.year
df['order_date'] = df['created'].dt.date
print("  ✅ Added time-based features")
print()

# Final stats
print("="*80)
print("📊 CLEANING RESULTS")
print("="*80)
print(f"Final shape: {df.shape}")
print(f"Total orders: {len(df):,}")
print(f"Anonymous orders (user_id=0): {(df['user_id'] == 0).sum():,}")
print(f"Registered orders (user_id>0): {(df['user_id'] > 0).sum():,}")
print(f"Unique registered customers: {df[df['user_id'] > 0]['user_id'].nunique():,}")
print()

# Save cleaned data
output_path = r'data\Inventory Management\fct_orders_cleaned_fixed.csv'
print(f"Saving to: {output_path}")
df.to_csv(output_path, index=False)
print("✅ File saved successfully!")
print()
print("⚠️  To replace the old file, close any programs using fct_orders.csv,")
print("    then rename fct_orders_cleaned_fixed.csv to fct_orders.csv")
print()

print("="*80)
print("🎯 CLEANING COMPLETE - Customer data preserved!")
print("="*80)
