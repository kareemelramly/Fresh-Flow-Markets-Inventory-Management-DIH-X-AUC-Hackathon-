# Fresh Flow Markets - Quick Start Guide for Cloud/Backend Team

## 🎯 Your Mission

You are responsible for:
1. **Database Setup** - Organizing data and creating the database
2. **API Development** - Building RESTful API endpoints
3. **Local Server** - Setting up local computer as a server
4. **ML Integration** - Connecting trained models with the backend

---

## 📁 What's Been Organized

### New Structure Created

```
Fresh-Flow-Markets-Inventory-Management/
├── database/                           # ← NEW! Database documentation
│   ├── DATABASE_SCHEMA.md             # Complete schema documentation
│   ├── ERD.md                         # Visual relationship diagrams
│   ├── setup_database.py              # Automated database setup script
│   └── README.md                      # Quick start for database
│
├── data/
│   └── Inventory Management/          # CSV files (already exists)
│       ├── dim_*.csv                  # Dimension tables
│       ├── fct_*.csv                  # Fact tables (transactions)
│       └── most_ordered.csv           # Pre-aggregated data
│
├── src/
│   ├── main.py                        # Application entry point
│   ├── api/
│   │   └── routes.py                  # API endpoint definitions
│   ├── models/
│   │   ├── data_loader.py            # Database connection
│   │   └── user_model.py             # Data models
│   ├── services/
│   │   └── inventory_service.py      # Business logic
│   └── utils/
│       └── helpers.py                 # Utility functions
│
└── requirements.txt                   # ← UPDATED with database packages
```

---

## 🚀 Step-by-Step Setup

### Step 1: Install Database (PostgreSQL Recommended)

**Windows:**
```powershell
# Download PostgreSQL installer
# https://www.postgresql.org/download/windows/
# Install with default settings

# Create database
createdb fresh_flow_inventory
```

**Alternative - MySQL:**
```powershell
# Download MySQL installer
# https://dev.mysql.com/downloads/installer/

# Create database
mysql -u root -p -e "CREATE DATABASE fresh_flow_inventory;"
```

### Step 2: Install Python Dependencies

```powershell
cd "c:\Users\mahmo\OneDrive\Desktop\D-Hackthon\Fresh-Flow-Markets-Inventory-Management-DIH-X-AUC-Hackathon-"

pip install -r requirements.txt
```

### Step 3: Load Data into Database

```powershell
# Run the automated setup script
python database/setup_database.py --db-type postgresql --user postgres --password yourpassword

# This will:
# ✅ Load all CSV files into database tables
# ✅ Create indexes for performance
# ✅ Set up analytical views
# ✅ Validate data integrity
```

### Step 4: Create Environment Variables

Create `.env` file in project root:

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
SECRET_KEY=your-secret-key-change-this-in-production

# ML Model Configuration
ML_MODEL_PATH=models/demand_forecast.pkl
```

### Step 5: Test Database Connection

```python
# test_connection.py
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Create connection
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Test query
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM dim_menu_items"))
    count = result.fetchone()[0]
    print(f"✅ Connection successful! Found {count} menu items.")
```

---

## 📊 Understanding the Data Structure

### Star Schema Design

The database follows a **star schema** pattern:

```
              dim_places (Center Hub)
                     │
         ┌───────────┼───────────┐
         │           │           │
   fct_orders   fct_campaigns   fct_inventory_reports
         │
   fct_order_items
         │
   dim_menu_items
         │
   dim_bill_of_materials
         │
      dim_skus
```

### Key Tables You'll Use Most

| Table | Type | Purpose | Use For |
|-------|------|---------|---------|
| `fct_orders` | Fact | Customer orders | Sales data, demand forecasting |
| `fct_order_items` | Fact | Order line items | What was sold |
| `dim_menu_items` | Dimension | Menu catalog | Product info |
| `dim_skus` | Dimension | Stock units | Current inventory levels |
| `dim_bill_of_materials` | Dimension | Recipes | Calculate ingredient needs |
| `dim_places` | Dimension | Merchants | Location filtering |

### Important Data Notes

1. **Timestamps are UNIX integers**
   ```sql
   -- Convert to readable date
   SELECT FROM_UNIXTIME(created) FROM fct_orders;
   ```

2. **Currency is DKK** (Danish Krone)
   - All price/amount fields are in DKK

3. **Filter Production Data**
   ```sql
   WHERE demo_mode = 0 AND trainee_mode = 0
   ```

4. **Multi-tenant** - Always filter by `place_id`
   ```sql
   WHERE place_id = 59897
   ```

---

## 🔌 Building Your API

### Recommended API Structure

```python
# src/api/routes.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Database connection
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ──────────────────────────────────────────────
# INVENTORY ENDPOINTS
# ──────────────────────────────────────────────

@app.route('/api/inventory/items', methods=['GET'])
def get_inventory_items():
    """Get all inventory items with current stock levels"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                s.id,
                s.title,
                s.quantity,
                s.low_stock_threshold,
                s.unit,
                sc.title as category,
                CASE 
                    WHEN s.quantity = 0 THEN 'OUT_OF_STOCK'
                    WHEN s.quantity <= s.low_stock_threshold THEN 'LOW_STOCK'
                    ELSE 'IN_STOCK'
                END as stock_status
            FROM dim_skus s
            LEFT JOIN dim_stock_categories sc ON s.stock_category_id = sc.id
            ORDER BY s.quantity ASC
        """))
        
        items = [dict(row) for row in result]
        return jsonify(items)

@app.route('/api/inventory/low-stock', methods=['GET'])
def get_low_stock_items():
    """Get items below reorder threshold"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT * FROM dim_skus
            WHERE quantity <= low_stock_threshold
            ORDER BY quantity ASC
        """))
        
        items = [dict(row) for row in result]
        return jsonify(items)

@app.route('/api/inventory/items/<int:item_id>/quantity', methods=['PUT'])
def update_quantity(item_id):
    """Update stock quantity (after restock or sale)"""
    data = request.json
    new_quantity = data.get('quantity')
    
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE dim_skus 
            SET quantity = :quantity,
                updated = UNIX_TIMESTAMP()
            WHERE id = :id
        """), {'quantity': new_quantity, 'id': item_id})
        conn.commit()
    
    return jsonify({'success': True, 'item_id': item_id})

# ──────────────────────────────────────────────
# MENU ENDPOINTS
# ──────────────────────────────────────────────

@app.route('/api/menu/items', methods=['GET'])
def get_menu_items():
    """Get all menu items"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                id,
                title,
                price,
                status,
                rating,
                purchases,
                section_id
            FROM dim_menu_items
            WHERE status = 'Active'
            ORDER BY purchases DESC
        """))
        
        items = [dict(row) for row in result]
        return jsonify(items)

@app.route('/api/menu/items/<int:item_id>/bom', methods=['GET'])
def get_item_recipe(item_id):
    """Get bill of materials (recipe) for a menu item"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                i.title as ingredient,
                bom.quantity as required_quantity,
                s.unit,
                s.quantity as current_stock
            FROM dim_bill_of_materials bom
            JOIN dim_skus s ON bom.sku_id = s.id
            JOIN dim_items i ON s.item_id = i.id
            WHERE bom.parent_sku_id = :item_id
        """), {'item_id': item_id})
        
        recipe = [dict(row) for row in result]
        return jsonify(recipe)

# ──────────────────────────────────────────────
# ORDER ENDPOINTS
# ──────────────────────────────────────────────

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get orders with optional filtering"""
    place_id = request.args.get('place_id')
    status = request.args.get('status')
    
    query = "SELECT * FROM fct_orders WHERE 1=1"
    params = {}
    
    if place_id:
        query += " AND place_id = :place_id"
        params['place_id'] = place_id
    
    if status:
        query += " AND status = :status"
        params['status'] = status
    
    query += " ORDER BY created DESC LIMIT 100"
    
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        orders = [dict(row) for row in result]
        return jsonify(orders)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    data = request.json
    
    with engine.connect() as conn:
        # Insert order
        result = conn.execute(text("""
            INSERT INTO fct_orders 
            (user_id, place_id, total_amount, type, channel, status, created, updated)
            VALUES 
            (:user_id, :place_id, :total_amount, :type, :channel, 'Pending', UNIX_TIMESTAMP(), UNIX_TIMESTAMP())
        """), data)
        
        order_id = result.lastrowid
        
        # Update inventory for each item
        for item in data.get('items', []):
            # Get BOM
            bom = conn.execute(text("""
                SELECT sku_id, quantity 
                FROM dim_bill_of_materials 
                WHERE parent_sku_id = :item_id
            """), {'item_id': item['item_id']})
            
            # Deduct from stock
            for ingredient in bom:
                conn.execute(text("""
                    UPDATE dim_skus 
                    SET quantity = quantity - :used_qty
                    WHERE id = :sku_id
                """), {
                    'used_qty': ingredient.quantity * item['quantity'],
                    'sku_id': ingredient.sku_id
                })
        
        conn.commit()
    
    return jsonify({'success': True, 'order_id': order_id})

# ──────────────────────────────────────────────
# ANALYTICS ENDPOINTS
# ──────────────────────────────────────────────

@app.route('/api/analytics/daily-sales', methods=['GET'])
def get_daily_sales():
    """Get daily sales summary"""
    days = request.args.get('days', 30)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                DATE(FROM_UNIXTIME(created)) as date,
                COUNT(*) as order_count,
                SUM(total_amount) as revenue,
                AVG(total_amount) as avg_order_value
            FROM fct_orders
            WHERE status = 'Closed'
                AND created >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL :days DAY))
            GROUP BY DATE(FROM_UNIXTIME(created))
            ORDER BY date DESC
        """), {'days': days})
        
        sales = [dict(row) for row in result]
        return jsonify(sales)

@app.route('/api/analytics/popular-items', methods=['GET'])
def get_popular_items():
    """Get most ordered items"""
    limit = request.args.get('limit', 10)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                mi.title,
                COUNT(oi.id) as order_count,
                SUM(oi.quantity) as total_sold
            FROM fct_order_items oi
            JOIN dim_menu_items mi ON oi.item_id = mi.id
            GROUP BY mi.id, mi.title
            ORDER BY total_sold DESC
            LIMIT :limit
        """), {'limit': limit})
        
        items = [dict(row) for row in result]
        return jsonify(items)

# ──────────────────────────────────────────────
# ML MODEL ENDPOINTS (To be integrated)
# ──────────────────────────────────────────────

@app.route('/api/ml/demand-forecast', methods=['GET'])
def get_demand_forecast():
    """Get demand predictions from ML model"""
    # TODO: Load trained model and make predictions
    # This is where you'll integrate your ML model
    return jsonify({'message': 'ML integration pending'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Run Your API Server

```powershell
python src/api/routes.py

# Server will start at: http://localhost:5000
# Test with: http://localhost:5000/api/inventory/items
```

---

## 🤖 ML Model Integration

### Where ML Models Fit

```
Frontend Request
     │
     ▼
  REST API
     │
     ▼
Database Query ────► Historical Data
     │                      │
     ▼                      ▼
ML Model Prediction ◄── Training Data
     │
     ▼
JSON Response
```

### Example: Demand Forecasting Integration

```python
# src/services/forecast_service.py
import joblib
import pandas as pd
from sqlalchemy import create_engine, text
import os

class DemandForecastService:
    def __init__(self):
        self.model = joblib.load(os.getenv('ML_MODEL_PATH'))
        self.engine = create_engine(f"postgresql://...")
    
    def predict_daily_demand(self, item_id, date):
        """Predict demand for a specific item on a specific date"""
        
        # Get historical features
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    AVG(quantity) as avg_qty_7d,
                    STDDEV(quantity) as std_qty_7d
                FROM fct_order_items oi
                JOIN fct_orders o ON oi.order_id = o.id
                WHERE oi.item_id = :item_id
                    AND o.created >= UNIX_TIMESTAMP(DATE_SUB(:date, INTERVAL 7 DAY))
            """), {'item_id': item_id, 'date': date})
            
            features = dict(result.fetchone())
        
        # Add temporal features
        features['day_of_week'] = pd.to_datetime(date).dayofweek
        features['is_weekend'] = 1 if features['day_of_week'] >= 5 else 0
        
        # Make prediction
        X = pd.DataFrame([features])
        prediction = self.model.predict(X)[0]
        
        return {
            'item_id': item_id,
            'date': date,
            'predicted_quantity': float(prediction),
            'confidence': 0.85  # From model
        }
```

---

## 🌐 Making Your Computer a Server

### For Local Testing (Development)

```powershell
# Run Flask API
python src/api/routes.py

# Access from same computer:
# http://localhost:5000/api/inventory/items

# Access from other devices on same network:
# http://YOUR_IP_ADDRESS:5000/api/inventory/items
# Find your IP: ipconfig (Windows)
```

### For Public Access (Production)

**Option 1: ngrok (Quick & Easy)**
```powershell
# Download ngrok: https://ngrok.com/download
# Install and authenticate

ngrok http 5000

# You'll get a public URL like:
# https://abc123.ngrok.io → http://localhost:5000
```

**Option 2: Deploy to Cloud (Recommended for hackathon)**
- **Heroku** (Free tier): Easy deployment
- **Railway** (Free tier): Modern alternative
- **AWS/Azure/GCP**: Professional option

---

## 📋 Testing Your Setup

### Health Check Endpoints

```python
@app.route('/health', methods=['GET'])
def health_check():
    """Check if API and database are working"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': pd.Timestamp.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

### Test with curl or Postman

```powershell
# Get inventory items
curl http://localhost:5000/api/inventory/items

# Get low stock items
curl http://localhost:5000/api/inventory/low-stock

# Update quantity
curl -X PUT http://localhost:5000/api/inventory/items/1/quantity `
     -H "Content-Type: application/json" `
     -d '{"quantity": 50}'
```

---

## 📚 Documentation You Created

1. **[database/DATABASE_SCHEMA.md](database/DATABASE_SCHEMA.md)**
   - Complete table definitions
   - Column descriptions
   - Relationships
   - ML integration guide
   - Sample queries

2. **[database/ERD.md](database/ERD.md)**
   - Visual relationship diagrams
   - Data flow charts
   - Index strategy

3. **[database/README.md](database/README.md)**
   - Quick start guide
   - Connection examples
   - Common queries

---

## ✅ Next Steps Checklist

- [ ] Install PostgreSQL/MySQL
- [ ] Run `pip install -r requirements.txt`
- [ ] Run `python database/setup_database.py`
- [ ] Create `.env` file with credentials
- [ ] Test database connection
- [ ] Build API endpoints (use examples above)
- [ ] Integrate ML models
- [ ] Create frontend to consume API
- [ ] Test end-to-end flow
- [ ] Deploy to cloud (optional but recommended)

---

## 🆘 Common Issues & Solutions

### Issue: "Connection refused" to database
**Solution:** 
```powershell
# Check if PostgreSQL is running
Get-Service postgresql*

# Start if stopped
Start-Service postgresql-x64-15  # Adjust version number
```

### Issue: "Table does not exist"
**Solution:** Run setup script again
```powershell
python database/setup_database.py
```

### Issue: "Permission denied"
**Solution:** Grant permissions
```sql
GRANT ALL PRIVILEGES ON DATABASE fresh_flow_inventory TO your_user;
```

---

## 📞 Resources

- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Flask Docs**: https://flask.palletsprojects.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

---

Good luck with your hackathon! 🚀
