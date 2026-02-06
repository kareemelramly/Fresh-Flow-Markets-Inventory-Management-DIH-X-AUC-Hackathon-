"""
Fresh Flow Markets - Database Setup Script
Loads all CSV files into SQLite database with proper schema
"""

import pandas as pd
import sqlite3
from pathlib import Path
import sys

def setup_database():
    print("=" * 80)
    print("FRESH FLOW MARKETS - DATABASE SETUP")
    print("=" * 80)
    
    # Database configuration
    db_path = "database/fresh_flow_markets.db"
    data_dir = Path("data/Inventory Management")
    
    # Create database connection
    print(f"\n[1/4] Creating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"   SUCCESS: Database created")
    
    # Get all CSV files
    csv_files = sorted(data_dir.glob("*.csv"))
    print(f"\n[2/4] Found {len(csv_files)} CSV files to import")
    
    # Load each CSV into database
    print(f"\n[3/4] Loading data into tables...")
    loaded_tables = []
    
    for csv_file in csv_files:
        table_name = csv_file.stem  # filename without extension
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            if len(df) == 0:
                print(f"   SKIP: {table_name} (empty file)")
                continue
            
            # Load into SQLite
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            print(f"   LOADED: {table_name:<30} ({len(df):>10,} rows, {len(df.columns):>3} cols)")
            loaded_tables.append({
                'table': table_name,
                'rows': len(df),
                'columns': len(df.columns)
            })
            
        except Exception as e:
            print(f"   ERROR: {table_name} - {str(e)[:60]}")
    
    # Create indexes for performance
    print(f"\n[4/4] Creating indexes for performance...")
    
    indexes = [
        # Primary key indexes
        "CREATE INDEX IF NOT EXISTS idx_dim_items_id ON dim_items(id)",
        "CREATE INDEX IF NOT EXISTS idx_dim_users_id ON dim_users(id)",
        "CREATE INDEX IF NOT EXISTS idx_dim_places_id ON dim_places(id)",
        "CREATE INDEX IF NOT EXISTS idx_dim_campaigns_id ON dim_campaigns(id)",
        "CREATE INDEX IF NOT EXISTS idx_dim_add_ons_id ON dim_add_ons(id)",
        
        # Foreign key indexes
        "CREATE INDEX IF NOT EXISTS idx_fct_orders_user_id ON fct_orders(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_fct_orders_place_id ON fct_orders(place_id)",
        "CREATE INDEX IF NOT EXISTS idx_fct_order_items_order_id ON fct_order_items(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_fct_order_items_item_id ON fct_order_items(item_id)",
        
        # Date indexes for analytics
        "CREATE INDEX IF NOT EXISTS idx_fct_orders_created ON fct_orders(created)",
        "CREATE INDEX IF NOT EXISTS idx_fct_order_items_created ON fct_order_items(created)",
    ]
    
    for idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
            index_name = idx_sql.split("idx_")[1].split(" ON")[0]
            print(f"   CREATED: idx_{index_name}")
        except Exception as e:
            print(f"   SKIP: {str(e)[:60]}")
    
    conn.commit()
    
    # Summary
    print("\n" + "=" * 80)
    print("DATABASE SETUP COMPLETE")
    print("=" * 80)
    
    print(f"\nDatabase: {db_path}")
    print(f"Tables loaded: {len(loaded_tables)}")
    print(f"Total rows: {sum(t['rows'] for t in loaded_tables):,}")
    
    print("\nTables:")
    for t in loaded_tables:
        print(f"  - {t['table']:<30} {t['rows']:>10,} rows")
    
    # Close connection
    conn.close()
    
    # Re-open for verification queries
    print("\n" + "=" * 80)
    print("VERIFICATION - Sample Queries")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        
        test_queries = [
            ("Total Orders", "SELECT COUNT(*) as count FROM fct_orders"),
            ("Total Order Items", "SELECT COUNT(*) as count FROM fct_order_items"),
            ("Total Users", "SELECT COUNT(*) as count FROM dim_users"),
            ("Total Places", "SELECT COUNT(*) as count FROM dim_places"),
            ("Total Items", "SELECT COUNT(*) as count FROM dim_items"),
        ]
        
        for name, query in test_queries:
            try:
                result = pd.read_sql_query(query, conn)
                print(f"{name}: {result['count'].iloc[0]:,}")
            except Exception as e:
                print(f"{name}: Could not verify")
        
        # Top 5 items
        print("\n" + "-" * 80)
        print("Top 5 Most Ordered Items:")
        print("-" * 80)
        try:
            top_items_query = """
            SELECT 
                i.title,
                COUNT(DISTINCT oi.order_id) as order_count,
                SUM(oi.quantity) as total_quantity
            FROM fct_order_items oi
            JOIN dim_items i ON oi.item_id = i.id
            WHERE i.title IS NOT NULL
            GROUP BY i.title
            ORDER BY order_count DESC
            LIMIT 5
            """
            top_items = pd.read_sql_query(top_items_query, conn)
            for idx, row in top_items.iterrows():
                print(f"  {idx+1}. {row['title']:<40} - {row['order_count']:>7,} orders ({row['total_quantity']:>8,} qty)")
        except Exception as e:
            print(f"  Top items verification skipped")
        
        conn.close()
    except Exception as e:
        print(f"Verification queries skipped (database is ready for use)")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Database ready for API integration")
    print("2. Run queries using: sqlite3 database/fresh_flow_markets.db")
    print("3. Connect to API: See CLOUD_BACKEND_GUIDE.md")
    print("4. Build ML models: See DATABASE_SCHEMA.md for features")
    print("=" * 80)

if __name__ == "__main__":
    try:
        setup_database()
        print("\n" + "=" * 80)
        print("✅ DATABASE SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n🚀 Your database is ready for use!")
        print("   - Start the API server: python app.py")
        print("   - Start the dashboard: streamlit run dashboard.py")
        print("\n")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user (Ctrl+C)")
        print("Note: If tables were loaded, the database may still be usable.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ DATABASE SETUP FAILED")
        print(f"Error: {str(e)}")
        print("\nTrying to diagnose the issue...")
        import traceback
        traceback.print_exc()
        print("\n")
        sys.exit(1)
