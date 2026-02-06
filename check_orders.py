import sqlite3
from datetime import datetime

conn = sqlite3.connect('database/fresh_flow_markets.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:")
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"  {t:<30} {count:>10,} rows")

print(f"\nTotal: {len(tables)} tables")

# Check for orders table that matches fct_orders pattern
orders_tables = [t for t in tables if 'order' in t.lower()]
print(f"\nOrder-related tables: {orders_tables}")

if orders_tables:
    for table_name in orders_tables:
        try:
            cursor.execute(f"SELECT MIN(created), MAX(created) FROM {table_name}")
            min_ts, max_ts = cursor.fetchone()
            if min_ts and max_ts:
                print(f"\n{table_name} date range:")
                print(f"  Earliest: {datetime.fromtimestamp(min_ts)}")
                print(f"  Latest: {datetime.fromtimestamp(max_ts)}")
                print(f"  Timestamps: {min_ts} to {max_ts}")
        except Exception as e:
            print(f"\n{table_name}: No 'created' column - {e}")

conn.close()
