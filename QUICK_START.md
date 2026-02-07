# Fresh Flow Markets - Quick Start Guide

## Step 1: Start the Services

### Terminal 1 - Start API:
```bash
python app.py
```
✓ Wait for: "Running on http://127.0.0.1:5000"

### Terminal 2 - Start Dashboard:
```bash
streamlit run dashboard.py
```
✓ Wait for: "Local URL: http://localhost:8501"

---

## Step 2: Verify Everything Works

### Test the API:
```bash
curl http://localhost:5000/health
```
Expected: `{"status": "healthy", "database": "connected"}`

### Test the Dashboard:
Open browser: http://localhost:8501
Expected: See "Fresh Flow Markets" dashboard with green theme

---

## Step 3: Use the System

### Option A: Use the Dashboard (Easiest)
1. Open http://localhost:8501
2. Navigate through tabs:
   - **Analytics Dashboard**: View stats
   - **Inventory Management**: Search items, check stock
   - **ML Forecasting**: Get demand predictions
   - **Campaign Predictions**: ROI forecasts
   - **Customer Churn**: Risk analysis

### Option B: Use the API (For Integration)
Base URL: http://localhost:5000

#### Get inventory items:
```bash
curl http://localhost:5000/api/inventory/items?limit=10
```

#### Get demand forecast:
```bash
curl -X POST http://localhost:5000/api/ml/forecast/demand \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "forecast_days": 7}'
```

#### Get campaign prediction:
```bash
curl -X POST http://localhost:5000/api/ml/campaigns/predict \
  -H "Content-Type: application/json" \
  -d '{"campaign_type": "Discount", "discount_percentage": 20, "duration_days": 7}'
```

#### Get customer churn risk:
```bash
curl -X POST http://localhost:5000/api/ml/customers/churn-risk \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1}'
```

### Option C: Website Integration Demo
1. Open `website_integration_demo.html` in browser
2. Click buttons to test API endpoints
3. See live responses from the API

---

## Step 4: Common Tasks

### Search for an item:
Dashboard → Inventory Management → Enter item ID or name

### Get forecast for an item:
Dashboard → ML Forecasting → Demand Forecast tab → Enter item ID

### Check low stock items:
Dashboard → Inventory Management → View "Low Stock Items"

### Predict campaign ROI:
Dashboard → Campaign Predictions → Enter campaign details

### Find at-risk customers:
Dashboard → Customer Churn → Enter customer ID

---

## API Documentation

Full API docs available at:
- Main docs: `docs/API_DOCUMENTATION.md`
- ML API docs: `docs/ML_API_DOCUMENTATION.md`
- Website integration: `docs/WEBSITE_INTEGRATION_GUIDE.md`

---

## Troubleshooting

### API not starting:
- Check if port 5000 is already in use
- Verify database exists: `database/fresh_flow_markets.db`
- Check Python dependencies: `pip install -r requirements.txt`

### Dashboard not loading:
- Check if port 8501 is available
- Verify `style.css` exists in root directory
- Check API is running (dashboard needs API)

### Stop all services:
```powershell
# Windows PowerShell
Get-NetTCPConnection -LocalPort 5000,8501 -ErrorAction SilentlyContinue | 
  Select-Object -ExpandProperty OwningProcess -Unique | 
  ForEach-Object { Stop-Process -Id $_ -Force }
```

---

## Next Steps for Development

1. **Test the forecasting**: Try different items and see predictions
2. **Explore the API**: Use Postman or curl to test endpoints
3. **Review ML models**: Check `ML_Models/` directory for available models
4. **Customize dashboard**: Edit `dashboard.py` to add features
5. **Integrate with website**: Use `website_integration_demo.html` as template
