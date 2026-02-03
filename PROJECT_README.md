# Fresh Flow Markets - Inventory Management System

**Deloitte Innovation Hub x AUC Hackathon 2026**

Complete cloud/backend solution for inventory management with REST API, analytics, and demand forecasting.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start API server
python app.py

# 3. Test the API
python test_api.py
```

**API runs at**: `http://localhost:5000`

---

## 📊 System Overview

### Database
- **Engine**: SQLite (622 MB)
- **Tables**: 18 (10 dimension + 8 fact tables)
- **Total Rows**: 2,705,091
- **Indexes**: 11 for optimal performance

### REST API
- **Framework**: Flask with CORS
- **Endpoints**: 11 across 5 categories
- **Features**: Pagination, filtering, real-time analytics

### Key Metrics
- **Orders**: 399,810
- **Order Items**: 1,999,341
- **Inventory Items**: 87,276
- **Active Places**: 793 restaurants

---

## 📁 Project Structure

```
Fresh-Flow-Markets-Inventory-Management/
│
├── app.py                      # API server entry point
├── test_api.py                 # API test & demonstration
├── setup_database.py           # Database initialization
├── requirements.txt            # Python dependencies
├── fresh_flow_markets.db       # Production database (622 MB)
│
├── src/
│   ├── api/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── routes.py          # 11 API endpoints
│   │   └── database.py        # Database utilities
│   └── models/
│       └── data_loader.py     # Data loading utilities
│
├── data/
│   └── Inventory Management/  # 19 cleaned CSV files
│
├── database/
│   ├── DATABASE_SCHEMA.md     # Complete schema documentation
│   ├── ERD.md                 # Entity relationship diagrams
│   └── setup_database.py      # Database setup script
│
├── docs/
│   ├── API_DOCUMENTATION.md   # Complete API reference
│   ├── CLOUD_BACKEND_GUIDE.md # Backend setup guide
│   └── GETTING_STARTED.md     # Detailed quick start
│
└── scripts/                    # Development scripts (not for production)
```

---

## 🔌 API Endpoints

### Inventory Management
```http
GET  /api/inventory/items          # List items (paginated)
GET  /api/inventory/items/:id      # Get item details
PUT  /api/inventory/items/:id      # Update item
GET  /api/inventory/low-stock      # Low stock alerts
```

### Orders
```http
GET  /api/orders                   # List orders (filtered)
GET  /api/orders/:id               # Order details with items
```

### Analytics
```http
GET  /api/analytics/dashboard      # Dashboard statistics
GET  /api/analytics/places         # Place performance
```

### Forecasting
```http
POST /api/forecast/demand          # ML demand prediction
```

### Places
```http
GET  /api/places                   # List active places
GET  /api/places/:id               # Place details
```

---

## 🧪 Testing

### Quick API Test
```bash
python test_api.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:5000/health

# Get inventory items
curl "http://localhost:5000/api/inventory/items?per_page=10"

# Dashboard analytics
curl "http://localhost:5000/api/analytics/dashboard?days=30"

# Demand forecast
curl -X POST http://localhost:5000/api/forecast/demand \
  -H "Content-Type: application/json" \
  -d '{"item_id": 123, "days": 7}'
```

---

## 💾 Database Schema

### Dimension Tables (Master Data)
- **dim_items** - 87,276 inventory items
- **dim_users** - 22,955 users
- **dim_places** - 1,824 restaurants/locations
- **dim_campaigns** - 641 marketing campaigns
- **dim_add_ons** - 9,731 item add-ons
- Plus 5 more dimension tables

### Fact Tables (Transactional Data)
- **fct_orders** - 399,810 orders
- **fct_order_items** - 1,999,341 line items
- **fct_cash_balances** - 52,915 transactions
- Plus 5 more fact tables

See [DATABASE_SCHEMA.md](database/DATABASE_SCHEMA.md) for complete documentation.

---

## 📈 Features

### 1. Real-Time Inventory Management
- Track stock levels across 87,276 items
- Low stock alerts and notifications
- Update inventory via API
- Search and filter by multiple criteria

### 2. Order Processing
- 399,810+ historical orders
- Order status tracking and filtering
- Detailed order line items
- Customer order history

### 3. Analytics Dashboard
- Revenue trends and forecasts
- Top-selling items analysis
- Order status breakdown
- Place/restaurant performance metrics

### 4. Demand Forecasting
- ML-based demand predictions
- Historical trend analysis
- Automated reorder recommendations
- 7-day forecasting window

---

## 🛠️ Development

### Prerequisites
- Python 3.12+
- pip package manager
- 1GB free disk space (for database)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd Fresh-Flow-Markets-Inventory-Management-DIH-X-AUC-Hackathon-

# Create virtual environment (optional)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running Locally
```bash
# Start API server
python app.py

# Server runs on http://localhost:5000
```

---

## 🚀 Production Deployment

### Using Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Waitress (Windows)
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### Environment Variables
```bash
export DATABASE_PATH=/path/to/fresh_flow_markets.db
export FLASK_ENV=production
```

---

## 📚 Documentation

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Complete setup instructions
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Full API reference
- **[Database Schema](database/DATABASE_SCHEMA.md)** - Complete database documentation
- **[Backend Guide](docs/CLOUD_BACKEND_GUIDE.md)** - Cloud/backend setup guide

---

## 🎯 Hackathon Deliverables

✅ **Database**: 2.7M rows, fully indexed and optimized  
✅ **REST API**: 11 production-ready endpoints  
✅ **Analytics**: Real-time dashboard with trends  
✅ **ML/AI**: Demand forecasting algorithm  
✅ **Documentation**: Complete technical documentation  
✅ **Testing**: Automated test suite  
✅ **Production Ready**: CORS-enabled, error handling, health monitoring  

---

## 👥 Team

**Cloud/Backend Team** - Fresh Flow Markets  
Deloitte Innovation Hub x AUC Hackathon 2026

---

## 📄 License

Built for educational purposes as part of the Deloitte x AUC Hackathon.

---

**Status**: ✅ Production Ready | **Database**: 2.7M rows | **API**: 11 endpoints | **Response Time**: <100ms
