# Database Setup & Management

This directory contains database schema documentation and setup scripts for the Fresh Flow Markets Inventory Management System.

## Quick Start

### 1. Install Dependencies

```bash
pip install pandas sqlalchemy psycopg2-binary pymysql python-dotenv
```

### 2. Set Up Database

#### Option A: PostgreSQL (Recommended)

```bash
# Install PostgreSQL
# Windows: Download from https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database
createdb fresh_flow_inventory

# Run setup script
python database/setup_database.py \
    --db-type postgresql \
    --host localhost \
    --user postgres \
    --password yourpassword \
    --database fresh_flow_inventory
```

#### Option B: MySQL

```bash
# Install MySQL
# Windows: Download from https://dev.mysql.com/downloads/installer/
# Mac: brew install mysql
# Linux: sudo apt-get install mysql-server

# Create database
mysql -u root -p -e "CREATE DATABASE fresh_flow_inventory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run setup script
python database/setup_database.py \
    --db-type mysql \
    --host localhost \
    --user root \
    --password yourpassword \
    --database fresh_flow_inventory
```

#### Option C: SQLite (Development Only)

```bash
# No installation needed - SQLite is built into Python
python database/setup_database.py --db-type sqlite --database fresh_flow_inventory
```

### 3. Verify Setup

The setup script will:
- ✅ Load all CSV files into database tables
- ✅ Create performance indexes
- ✅ Set up analytical views
- ✅ Run data validation checks
- ✅ Display table statistics

You should see output like:

```
================================================================
Fresh Flow Markets - Database Setup
================================================================

📁 Loading CSV files into database...

Loading dim_items... ✓ Loaded 1,234 rows
Loading dim_skus... ✓ Loaded 567 rows
...

📊 Creating indexes...
  ✓ Created index for dim_skus
  ✓ Created index for fct_orders
  ...

✓ Database setup complete!
================================================================
```

## Files in This Directory

| File | Description |
|------|-------------|
| `DATABASE_SCHEMA.md` | Complete database schema documentation with table descriptions, relationships, and ML integration guide |
| `setup_database.py` | Automated database setup script that loads CSV files and creates indexes |
| `README.md` | This file - quick start guide |

## Database Schema Overview

### Core Structure

```
📊 DIMENSION TABLES (Master Data)
├── dim_items - Inventory items catalog
├── dim_skus - Stock keeping units with quantities
├── dim_stock_categories - Inventory categories
├── dim_bill_of_materials - Recipe ingredient breakdown
├── dim_menu_items - Sellable menu products
├── dim_add_ons - Product modifiers
├── dim_places - Merchant locations
├── dim_users - Staff and customers
└── dim_taxonomy_terms - Global lookup tables

📈 FACT TABLES (Transactional Data)
├── fct_orders - Customer orders
├── fct_order_items - Order line items
├── fct_inventory_reports - Stock level reports
├── fct_cash_balances - Cash drawer reconciliation
├── fct_invoice_items - Platform invoicing
├── fct_bonus_codes - Promotional codes
└── fct_campaigns - Campaign execution data

📋 VIEWS (Pre-computed Analytics)
└── most_ordered - Top selling items by location
```

### Key Relationships

```
dim_places (Merchants)
    ↓
fct_orders (Orders)
    ↓
fct_order_items (Line Items)
    ↓
dim_menu_items (Menu)
    ↓
dim_bill_of_materials (Recipes)
    ↓
dim_skus (Stock Units)
```

## Connecting Your Application

### Python (SQLAlchemy)

```python
from sqlalchemy import create_engine

# PostgreSQL
engine = create_engine('postgresql://user:password@localhost/fresh_flow_inventory')

# MySQL
engine = create_engine('mysql+pymysql://user:password@localhost/fresh_flow_inventory')

# SQLite
engine = create_engine('sqlite:///fresh_flow_inventory.db')

# Execute queries
import pandas as pd
df = pd.read_sql("SELECT * FROM dim_menu_items LIMIT 10", engine)
```

### Python (psycopg2 - PostgreSQL)

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="fresh_flow_inventory",
    user="postgres",
    password="yourpassword"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM dim_menu_items LIMIT 10")
rows = cursor.fetchall()
```

### Node.js (pg)

```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  database: 'fresh_flow_inventory',
  user: 'postgres',
  password: 'yourpassword',
  port: 5432
});

// Query
pool.query('SELECT * FROM dim_menu_items LIMIT 10', (err, res) => {
  console.log(res.rows);
});
```

## Environment Variables

Create a `.env` file in your project root:

```env
# Database Configuration
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fresh_flow_inventory
DB_USER=postgres
DB_PASSWORD=yourpassword

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
SECRET_KEY=your-secret-key-here

# ML Model Configuration
ML_MODEL_PATH=models/demand_forecast.pkl
ML_RETRAIN_INTERVAL=daily
```

## Common Queries

### Get Low Stock Items

```sql
SELECT 
    s.title,
    s.quantity,
    s.low_stock_threshold,
    s.unit,
    sc.title as category
FROM dim_skus s
JOIN dim_stock_categories sc ON s.stock_category_id = sc.id
WHERE s.quantity <= s.low_stock_threshold
ORDER BY s.quantity ASC;
```

### Daily Sales Report

```sql
SELECT 
    DATE(FROM_UNIXTIME(created)) as date,
    COUNT(*) as order_count,
    SUM(total_amount) as revenue,
    AVG(total_amount) as avg_order_value
FROM fct_orders
WHERE status = 'Closed'
    AND created >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 30 DAY))
GROUP BY DATE(FROM_UNIXTIME(created))
ORDER BY date DESC;
```

### Most Popular Items This Week

```sql
SELECT 
    mi.title,
    COUNT(oi.id) as order_count,
    SUM(oi.quantity) as total_sold,
    SUM(oi.price * oi.quantity) as revenue
FROM fct_order_items oi
JOIN dim_menu_items mi ON oi.item_id = mi.id
JOIN fct_orders o ON oi.order_id = o.id
WHERE o.created >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 7 DAY))
    AND o.status = 'Closed'
GROUP BY mi.id, mi.title
ORDER BY total_sold DESC
LIMIT 10;
```

### Calculate Required Ingredients for Forecasted Demand

```sql
SELECT 
    i.title as ingredient,
    SUM(bom.quantity * oi.quantity) as required_qty,
    s.unit,
    s.quantity as current_stock
FROM fct_order_items oi
JOIN dim_bill_of_materials bom ON oi.item_id = bom.parent_sku_id
JOIN dim_skus s ON bom.sku_id = s.id
JOIN dim_items i ON s.item_id = i.id
JOIN fct_orders o ON oi.order_id = o.id
WHERE o.created >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 1 DAY))
GROUP BY i.id, i.title, s.unit, s.quantity;
```

## Data Maintenance

### Backup Database

```bash
# PostgreSQL
pg_dump fresh_flow_inventory > backup_$(date +%Y%m%d).sql

# MySQL
mysqldump -u root -p fresh_flow_inventory > backup_$(date +%Y%m%d).sql

# SQLite
sqlite3 fresh_flow_inventory.db ".backup backup_$(date +%Y%m%d).db"
```

### Restore Database

```bash
# PostgreSQL
psql fresh_flow_inventory < backup_20260203.sql

# MySQL
mysql -u root -p fresh_flow_inventory < backup_20260203.sql

# SQLite
sqlite3 fresh_flow_inventory.db ".restore backup_20260203.db"
```

### Update Statistics (PostgreSQL)

```sql
VACUUM ANALYZE;
```

## Troubleshooting

### Connection Refused

```bash
# Check if database is running
# PostgreSQL
sudo service postgresql status

# MySQL
sudo service mysql status
```

### Permission Denied

```sql
-- Grant permissions to user
GRANT ALL PRIVILEGES ON DATABASE fresh_flow_inventory TO your_user;
```

### Out of Memory During Import

Reduce chunk size in `setup_database.py`:

```python
chunk_size=5000  # Default is 10000
```

### Slow Queries

1. Check if indexes are created: `\di` in psql
2. Run EXPLAIN on slow queries
3. Consider adding more indexes based on query patterns

## Next Steps

1. ✅ **Database is set up** - You can now connect your API
2. 📝 **Read** [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for complete table documentation
3. 🔌 **Build API** endpoints using Flask/FastAPI/Django
4. 🤖 **Train ML models** using the data for demand forecasting
5. 🌐 **Create frontend** that consumes your API

## Support

For detailed schema information, see [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)

For questions about the project, refer to the main [README.md](../README.md)
