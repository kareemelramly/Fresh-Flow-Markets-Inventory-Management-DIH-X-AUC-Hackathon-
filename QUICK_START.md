# Fresh Flow Markets - Quick Start Guide

## 🚀 Setup Steps

### 1. Install PostgreSQL

**Option A: PostgreSQL (Recommended for Production)**
```powershell
# Download PostgreSQL 16 from:
# https://www.postgresql.org/download/windows/

# During installation, set:
# - Password: (choose a strong password)
# - Port: 5432 (default)
# - Locale: Default
```

**Option B: SQLite (Quick Start - No Installation)**
```powershell
# SQLite comes with Python - no installation needed!
# Perfect for development and testing
```

### 2. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Set Up Database

**For PostgreSQL:**
```powershell
# Edit connection details in setup script
python database/setup_database.py --db-type postgresql --user postgres --password YOUR_PASSWORD
```

**For SQLite (Quick Start):**
```powershell
# Creates freshflow.db in project root - no configuration needed!
python database/setup_database.py --db-type sqlite
```

This will:
- ✅ Create all 19 tables from CSV files
- ✅ Set up indexes for fast queries
- ✅ Create analytical views
- ✅ Validate data integrity
- ✅ Generate connection details

### 4. Start API Server

```powershell
python src/main.py
```

API will be available at: `http://localhost:5000`

### 5. Test the API

```powershell
# Get inventory summary
curl http://localhost:5000/api/inventory/summary

# Get top ordered items
curl http://localhost:5000/api/analytics/top-items?limit=10

# Demand forecast
curl http://localhost:5000/api/ml/demand-forecast?item_id=123
```

## 📊 Database Schema

See [database/DATABASE_SCHEMA.md](database/DATABASE_SCHEMA.md) for complete schema documentation.

**Quick Overview:**
- **10 Dimension Tables**: Master data (items, users, places, campaigns)
- **8 Fact Tables**: Transactional data (orders, inventory, cash balances)
- **1 Aggregated View**: Most ordered items

**Key Tables:**
- `fct_orders` - 400K orders
- `fct_order_items` - 2M order line items
- `dim_users` - 23K users
- `dim_items` - 87K menu items
- `dim_places` - 1.8K restaurant locations

## 🔧 Development Tools

### Check Database Connection
```powershell
python -c "from database.setup_database import test_connection; test_connection()"
```

### View Sample Data
```powershell
python -c "import pandas as pd; print(pd.read_csv('data/Inventory Management/fct_orders.csv').head())"
```

### Run Quality Checks
```powershell
python fix_all_quality_issues.py
```

## 📚 Additional Documentation

- [DATABASE_SCHEMA.md](database/DATABASE_SCHEMA.md) - Complete schema reference
- [CLOUD_BACKEND_GUIDE.md](CLOUD_BACKEND_GUIDE.md) - API development guide
- [DATA_CLEANING_SUMMARY.md](DATA_CLEANING_SUMMARY.md) - Data quality report
- [database/ERD.md](database/ERD.md) - Visual diagrams

## 🆘 Troubleshooting

**Database connection fails:**
```powershell
# Check PostgreSQL is running
Get-Service postgresql*

# Restart PostgreSQL service
Restart-Service postgresql-x64-16
```

**Import errors:**
```powershell
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Port already in use:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /F /PID <PID>
```

## 💡 Next Steps

1. ✅ Database is set up
2. 📊 Build analytics dashboards
3. 🤖 Train ML models for demand forecasting
4. 🔌 Create API endpoints for frontend
5. 🚀 Deploy to cloud (AWS/Azure/GCP)

See [CLOUD_BACKEND_GUIDE.md](CLOUD_BACKEND_GUIDE.md) for deployment instructions.
