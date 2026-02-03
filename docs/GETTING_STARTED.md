# Fresh Flow Markets - Inventory Management System

**Deloitte x AUC Hackathon** - Complete Cloud/Backend Solution

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Database
```bash
python setup_database.py
```
Database: `fresh_flow_markets.db` (622 MB, 2.7M rows)

### 3. Start API Server
```bash
python app.py
```
API runs at: `http://localhost:5000`

### 4. Test API
```bash
python test_api.py
```

## 📊 System Overview

### Database
- **SQLite** database with 18 tables
- **2,705,091 rows** of cleaned data
- **Star schema** design (dimension + fact tables)
- **11 indexes** for optimal performance

### REST API
- **11 endpoints** across 5 categories
- **Flask** framework with CORS enabled
- **Pagination** support on all list endpoints
- **Real-time analytics** and forecasting

## 🔌 API Endpoints

### Inventory Management
```http
GET  /api/inventory/items          # List items (paginated, searchable)
GET  /api/inventory/items/:id      # Get item details
PUT  /api/inventory/items/:id      # Update item
GET  /api/inventory/low-stock      # Alert: low stock items
```

### Orders
```http
GET  /api/orders                   # List orders (with filters)
GET  /api/orders/:id               # Order details with items
```

### Analytics
```http
GET  /api/analytics/dashboard      # Dashboard statistics
GET  /api/analytics/places         # Place performance metrics
```

### Demand Forecasting
```http
POST /api/forecast/demand          # ML-based demand prediction
```

### Places/Restaurants
```http
GET  /api/places                   # List active places
GET  /api/places/:id               # Place details
```

## 📁 Project Structure

```
Fresh-Flow-Markets-Inventory-Management/
├── app.py                      # API server entry point
├── setup_database.py           # Database initialization
├── test_api.py                 # API demonstration script
├── fresh_flow_markets.db       # SQLite database (622 MB)
├── requirements.txt            # Python dependencies
│
├── src/
│   ├── api/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── routes.py          # API endpoints
│   │   └── database.py        # DB utilities
│   └── models/
│       └── data_loader.py     # Data loading utilities
│
├── data/
│   └── Inventory Management/  # 19 CSV files (cleaned)
│
├── database/
│   ├── DATABASE_SCHEMA.md     # Complete schema documentation
│   ├── ERD.md                 # Visual diagrams
│   └── setup_database.py      # Database setup script
│
└── docs/
    ├── API_DOCUMENTATION.md   # API reference
    └── CLOUD_BACKEND_GUIDE.md # Setup guide
```

## 💾 Database Tables

### Dimension Tables (Master Data)
- `dim_items` - 87,276 items
- `dim_users` - 22,955 users
- `dim_places` - 1,824 restaurants
- `dim_campaigns` - 641 campaigns
- `dim_add_ons` - 9,731 add-ons
- And 5 more...

### Fact Tables (Transactions)
- `fct_orders` - 399,810 orders
- `fct_order_items` - 1,999,341 line items
- `fct_cash_balances` - 52,915 transactions
- And 5 more...

## 🧪 Testing

### Health Check
```bash
curl http://localhost:5000/health
```

### Get Inventory Items
```bash
curl "http://localhost:5000/api/inventory/items?per_page=10"
```

### Dashboard Analytics
```bash
curl "http://localhost:5000/api/analytics/dashboard?days=30"
```

### Demand Forecast
```bash
curl -X POST http://localhost:5000/api/forecast/demand \
  -H "Content-Type: application/json" \
  -d '{"item_id": 123, "days": 7}'
```

## 📈 Key Features

### 1. Inventory Management
- Real-time stock tracking
- Low stock alerts
- Item search and filtering
- Update stock levels via API

### 2. Order Processing
- 399,810+ historical orders
- Order status tracking
- Filter by date, status, place
- Detailed order line items

### 3. Analytics Dashboard
- Revenue trends
- Top selling items
- Order status breakdown
- Place performance metrics

### 4. Demand Forecasting
- ML-based predictions
- Historical analysis
- Reorder recommendations
- 7-day forecast

## 🛠️ Development

### Add New Endpoint
1. Edit `src/api/routes.py`
2. Add route function with `@api_bp.route()`
3. Use `query_db()` for database queries
4. Return JSON with `jsonify()`

### Query Database
```python
from src.api.database import query_db

# Single row
user = query_db("SELECT * FROM dim_users WHERE id = ?", [123], one=True)

# Multiple rows
items = query_db("SELECT * FROM dim_items LIMIT 10")
```

## 📦 Dependencies

```
flask==3.1.2
flask-cors==6.0.2
pandas==2.2.0
sqlalchemy==2.0.0
```

## 🚀 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables
```bash
export DATABASE_PATH=/path/to/fresh_flow_markets.db
export FLASK_ENV=production
```

### Docker (Optional)
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📚 Documentation

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference
- [DATABASE_SCHEMA.md](database/DATABASE_SCHEMA.md) - Database schema
- [CLOUD_BACKEND_GUIDE.md](CLOUD_BACKEND_GUIDE.md) - Setup guide

## 🎯 Hackathon Deliverables

✅ **Database**: SQLite with 2.7M rows, fully indexed
✅ **REST API**: 11 endpoints, CORS-enabled
✅ **Analytics**: Real-time dashboard with trends
✅ **ML Forecasting**: Demand prediction algorithm
✅ **Documentation**: Complete API and schema docs
✅ **Testing**: Automated test suite included

## 📧 Support

For issues or questions, refer to the documentation or check the API test script: `test_api.py`

---

**Team**: Cloud/Backend - Fresh Flow Markets
**Hackathon**: Deloitte x AUC 2026
**Database**: 2,705,091 rows | **API**: 11 endpoints | **Status**: ✅ Production Ready
