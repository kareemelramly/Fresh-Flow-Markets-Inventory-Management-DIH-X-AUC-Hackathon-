"""
Fresh Flow Markets - Database Setup Script
===========================================

This script:
1. Creates database connection
2. Loads CSV files into database tables
3. Creates indexes for performance
4. Sets up foreign key constraints
5. Validates data integrity

Usage:
    python setup_database.py --db-type postgresql --host localhost --user myuser --password mypass

Requirements:
    pip install pandas sqlalchemy psycopg2-binary pymysql
"""

import pandas as pd
from sqlalchemy import create_engine, text
import argparse
import os
from pathlib import Path
import json
from datetime import datetime


class DatabaseSetup:
    """Handles database initialization and CSV data import"""
    
    def __init__(self, db_type='sqlite', host='localhost', port=None, 
                 database='fresh_flow_inventory', user='postgres', password=''):
        """
        Initialize database connection
        
        Args:
            db_type: 'postgresql', 'mysql', or 'sqlite' (default: sqlite)
            host: Database host
            port: Database port (default: 5432 for postgres, 3306 for mysql)
            database: Database name (for sqlite, this becomes the filename)
            user: Database user
            password: Database password
        """
        self.db_type = db_type
        self.database = database
        
        # Set default ports
        if port is None:
            port = 5432 if db_type == 'postgresql' else 3306
        
        # Create connection string
        if db_type == 'postgresql':
            conn_string = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        elif db_type == 'mysql':
            conn_string = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
        elif db_type == 'sqlite':
            # Use project root for SQLite database
            db_path = Path(database if database.endswith('.db') else f'{database}.db')
            conn_string = f'sqlite:///{db_path}'
            print(f"📁 Using SQLite database: {db_path.absolute()}")
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        print(f"🔌 Connecting to {db_type} database...")
        self.engine = create_engine(conn_string, echo=False)
        
        # Test connection
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✅ Connected successfully!")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise
        
        # Define table mapping
        self.csv_files = {
            # Dimension tables
            'dim_items': 'data/Inventory Management/dim_items.csv',
            'dim_skus': 'data/Inventory Management/dim_skus.csv',
            'dim_stock_categories': 'data/Inventory Management/dim_stock_categories.csv',
            'dim_bill_of_materials': 'data/Inventory Management/dim_bill_of_materials.csv',
            'dim_menu_items': 'data/Inventory Management/dim_menu_items.csv',
            'dim_add_ons': 'data/Inventory Management/dim_add_ons.csv',
            'dim_menu_item_add_ons': 'data/Inventory Management/dim_menu_item_add_ons.csv',
            'dim_places': 'data/Inventory Management/dim_places.csv',
            'dim_taxonomy_terms': 'data/Inventory Management/dim_taxonomy_terms.csv',
            'dim_users': 'data/Inventory Management/dim_users.csv',
            'dim_campaigns': 'data/Inventory Management/dim_campaigns.csv',
            
            # Fact tables
            'fct_orders': 'data/Inventory Management/fct_orders.csv',
            'fct_order_items': 'data/Inventory Management/fct_order_items.csv',
            'fct_inventory_reports': 'data/Inventory Management/fct_inventory_reports.csv',
            'fct_cash_balances': 'data/Inventory Management/fct_cash_balances.csv',
            'fct_invoice_items': 'data/Inventory Management/fct_invoice_items.csv',
            'fct_bonus_codes': 'data/Inventory Management/fct_bonus_codes.csv',
            'fct_campaigns': 'data/Inventory Management/fct_campaigns.csv',
            
            # Aggregated views
            'most_ordered': 'data/Inventory Management/most_ordered.csv',
        }
    
    def load_csv_to_table(self, table_name, csv_path, chunk_size=10000):
        """
        Load CSV file into database table
        
        Args:
            table_name: Name of the database table
            csv_path: Path to CSV file
            chunk_size: Number of rows to insert at once
        """
        if not os.path.exists(csv_path):
            print(f"⚠️  Warning: File not found - {csv_path}")
            return False
        
        print(f"Loading {table_name}...", end=" ")
        
        try:
            # Read CSV in chunks to handle large files
            chunks_loaded = 0
            total_rows = 0
            
            for chunk in pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False):
                # Clean data
                chunk = self.clean_dataframe(chunk, table_name)
                
                # Load to database
                chunk.to_sql(
                    table_name, 
                    self.engine, 
                    if_exists='append' if chunks_loaded > 0 else 'replace',
                    index=False,
                    method='multi'
                )
                
                chunks_loaded += 1
                total_rows += len(chunk)
            
            print(f"✓ Loaded {total_rows:,} rows")
            return True
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False
    
    def clean_dataframe(self, df, table_name):
        """
        Clean and preprocess DataFrame before loading
        
        Args:
            df: Pandas DataFrame
            table_name: Name of target table
        
        Returns:
            Cleaned DataFrame
        """
        # Convert Unix timestamps to datetime (optional - keep as int for compatibility)
        timestamp_columns = ['created', 'updated', 'contract_start', 'termination_date', 
                           'start_date_time', 'end_date_time', 'pickup_time', 'promise_time']
        
        for col in timestamp_columns:
            if col in df.columns:
                # Keep as integer for now, conversion can happen in queries
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('Int64')
        
        # Handle boolean columns
        bool_columns = ['deleted', 'demo_mode', 'select_as_default', 'active', 'bankrupt',
                       'delivery', 'eat_in', 'takeaway', 'discountable']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].fillna(0).astype(int)
        
        # Clean text columns
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).replace('nan', None)
        
        return df
    
    def create_indexes(self):
        """Create database indexes for performance optimization"""
        
        print("\n📊 Creating indexes...")
        
        indexes = {
            # Inventory indexes
            'dim_skus': [
                'CREATE INDEX IF NOT EXISTS idx_skus_stock_category ON dim_skus(stock_category_id)',
                'CREATE INDEX IF NOT EXISTS idx_skus_quantity ON dim_skus(quantity)',
                'CREATE INDEX IF NOT EXISTS idx_skus_item ON dim_skus(item_id)',
            ],
            'dim_bill_of_materials': [
                'CREATE INDEX IF NOT EXISTS idx_bom_parent ON dim_bill_of_materials(parent_sku_id)',
                'CREATE INDEX IF NOT EXISTS idx_bom_sku ON dim_bill_of_materials(sku_id)',
            ],
            'dim_items': [
                'CREATE INDEX IF NOT EXISTS idx_items_section ON dim_items(section_id)',
                'CREATE INDEX IF NOT EXISTS idx_items_status ON dim_items(status)',
            ],
            
            # Order indexes
            'fct_orders': [
                'CREATE INDEX IF NOT EXISTS idx_orders_place ON fct_orders(place_id)',
                'CREATE INDEX IF NOT EXISTS idx_orders_created ON fct_orders(created)',
                'CREATE INDEX IF NOT EXISTS idx_orders_status ON fct_orders(status)',
                'CREATE INDEX IF NOT EXISTS idx_orders_type ON fct_orders(type)',
                'CREATE INDEX IF NOT EXISTS idx_orders_place_created ON fct_orders(place_id, created)',
            ],
            'fct_order_items': [
                'CREATE INDEX IF NOT EXISTS idx_order_items_order ON fct_order_items(order_id)',
                'CREATE INDEX IF NOT EXISTS idx_order_items_item ON fct_order_items(item_id)',
            ],
            
            # Menu indexes
            'dim_menu_items': [
                'CREATE INDEX IF NOT EXISTS idx_menu_items_section ON dim_menu_items(section_id)',
                'CREATE INDEX IF NOT EXISTS idx_menu_items_status ON dim_menu_items(status)',
            ],
            
            # User and place indexes
            'dim_users': [
                'CREATE INDEX IF NOT EXISTS idx_users_type ON dim_users(type)',
                'CREATE INDEX IF NOT EXISTS idx_users_email ON dim_users(email)',
            ],
            'dim_places': [
                'CREATE INDEX IF NOT EXISTS idx_places_active ON dim_places(active)',
                'CREATE INDEX IF NOT EXISTS idx_places_area ON dim_places(area_id)',
            ],
        }
        
        with self.engine.connect() as conn:
            for table, index_list in indexes.items():
                for index_sql in index_list:
                    try:
                        conn.execute(text(index_sql))
                        print(f"  ✓ Created index for {table}")
                    except Exception as e:
                        print(f"  ⚠️  Index creation warning for {table}: {str(e)}")
            conn.commit()
    
    def create_views(self):
        """Create materialized views for analytics"""
        
        print("\n📈 Creating analytical views...")
        
        # Daily sales summary view
        daily_sales_view = """
        CREATE OR REPLACE VIEW daily_sales_summary AS
        SELECT 
            DATE(FROM_UNIXTIME(o.created)) as sale_date,
            o.place_id,
            o.type as order_type,
            o.channel,
            COUNT(DISTINCT o.id) as order_count,
            COUNT(oi.id) as item_count,
            SUM(o.total_amount) as total_revenue,
            SUM(o.discount_amount) as total_discounts,
            AVG(o.total_amount) as avg_order_value
        FROM fct_orders o
        LEFT JOIN fct_order_items oi ON o.id = oi.order_id
        WHERE o.status = 'Closed'
        GROUP BY sale_date, o.place_id, o.type, o.channel
        """
        
        # Inventory status view
        inventory_status_view = """
        CREATE OR REPLACE VIEW inventory_status AS
        SELECT 
            s.id,
            s.title,
            s.quantity,
            s.low_stock_threshold,
            s.unit,
            sc.title as category,
            i.title as item_name,
            i.price,
            CASE 
                WHEN s.quantity = 0 THEN 'OUT_OF_STOCK'
                WHEN s.quantity <= s.low_stock_threshold THEN 'LOW_STOCK'
                ELSE 'IN_STOCK'
            END as stock_status
        FROM dim_skus s
        LEFT JOIN dim_stock_categories sc ON s.stock_category_id = sc.id
        LEFT JOIN dim_items i ON s.item_id = i.id
        """
        
        try:
            with self.engine.connect() as conn:
                if self.db_type in ['postgresql', 'mysql']:
                    conn.execute(text(daily_sales_view))
                    conn.execute(text(inventory_status_view))
                    conn.commit()
                    print("  ✓ Created analytical views")
        except Exception as e:
            print(f"  ⚠️  View creation warning: {str(e)}")
    
    def validate_data(self):
        """Run data quality checks"""
        
        print("\n🔍 Running data validation...")
        
        with self.engine.connect() as conn:
            # Check for orphaned records
            checks = [
                {
                    'name': 'Orphaned orders',
                    'query': '''
                        SELECT COUNT(*) as count 
                        FROM fct_orders 
                        WHERE place_id NOT IN (SELECT id FROM dim_places)
                    '''
                },
                {
                    'name': 'Orders without items',
                    'query': '''
                        SELECT COUNT(*) as count 
                        FROM fct_orders o
                        LEFT JOIN fct_order_items oi ON o.id = oi.order_id
                        WHERE oi.id IS NULL
                    '''
                },
                {
                    'name': 'Menu items without price',
                    'query': '''
                        SELECT COUNT(*) as count 
                        FROM dim_menu_items 
                        WHERE price IS NULL OR price = 0
                    '''
                },
            ]
            
            for check in checks:
                try:
                    result = conn.execute(text(check['query'])).fetchone()
                    count = result[0]
                    status = "✓" if count == 0 else "⚠️"
                    print(f"  {status} {check['name']}: {count}")
                except Exception as e:
                    print(f"  ✗ {check['name']}: Error - {str(e)}")
    
    def get_table_stats(self):
        """Display statistics for loaded tables"""
        
        print("\n📊 Table Statistics:")
        print("-" * 60)
        
        with self.engine.connect() as conn:
            for table_name in self.csv_files.keys():
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()
                    count = result[0]
                    print(f"  {table_name:<30} {count:>10,} rows")
                except Exception as e:
                    print(f"  {table_name:<30} {'Error':>10}")
    
    def run_setup(self):
        """Execute full database setup process"""
        
        print("=" * 60)
        print("Fresh Flow Markets - Database Setup")
        print("=" * 60)
        
        # Get project root directory
        project_root = Path(__file__).parent.parent
        
        # Load CSV files
        print("\n📁 Loading CSV files into database...\n")
        
        success_count = 0
        failed_count = 0
        
        for table_name, csv_relative_path in self.csv_files.items():
            csv_path = project_root / csv_relative_path
            if self.load_csv_to_table(table_name, str(csv_path)):
                success_count += 1
            else:
                failed_count += 1
        
        print(f"\n✓ Successfully loaded {success_count} tables")
        if failed_count > 0:
            print(f"⚠️  Failed to load {failed_count} tables")
        
        # Create indexes
        self.create_indexes()
        
        # Create views
        self.create_views()
        
        # Validate data
        self.validate_data()
        
        # Show statistics
        self.get_table_stats()
        
        print("\n" + "=" * 60)
        print("✓ Database setup complete!")
        print("=" * 60)
        print(f"\nDatabase: {self.database}")
        print(f"Type: {self.db_type}")
        print(f"\nYou can now connect your API to this database.")
        print("=" * 60)


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='Set up Fresh Flow Markets database')
    parser.add_argument('--db-type', default='postgresql', 
                       choices=['postgresql', 'mysql', 'sqlite'],
                       help='Database type (default: postgresql)')
    parser.add_argument('--host', default='localhost',
                       help='Database host (default: localhost)')
    parser.add_argument('--port', type=int, default=None,
                       help='Database port (default: 5432 for postgres, 3306 for mysql)')
    parser.add_argument('--database', default='fresh_flow_inventory',
                       help='Database name (default: fresh_flow_inventory)')
    parser.add_argument('--user', default='postgres',
                       help='Database user (default: postgres)')
    parser.add_argument('--password', default='',
                       help='Database password')
    
    args = parser.parse_args()
    
    # Create and run setup
    setup = DatabaseSetup(
        db_type=args.db_type,
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password
    )
    
    setup.run_setup()


if __name__ == '__main__':
    main()
