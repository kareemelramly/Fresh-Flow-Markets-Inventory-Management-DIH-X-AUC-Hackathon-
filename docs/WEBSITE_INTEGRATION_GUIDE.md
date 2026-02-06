# Fresh Flow Markets - Website Integration Guide

## Overview

This guide explains how to integrate the Fresh Flow Markets ML Prediction API with your upcoming website/dashboard.

**API Version**: 2.0  
**Status**: ✅ Ready for Integration  
**Database**: ✅ 90% Ready (minor enhancements recommended)  
**CORS**: ✅ Configured for web applications

---

## Quick Start

### 1. Start the API Server

```bash
# Navigate to project directory
cd Fresh-Flow-Markets-Inventory-Management-DIH-X-AUC-Hackathon

# Activate Python environment (if using venv)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

Server will start on: `http://localhost:5000`

### 2. Verify API is Running

```bash
# Health check
curl http://localhost:5000/health

# ML service check
curl http://localhost:5000/api/ml/health

# Get available models
curl http://localhost:5000/api/ml/models/status
```

### 3. Test a Prediction

```bash
# Test campaign prediction
curl -X POST http://localhost:5000/api/ml/campaigns/predict \
  -H "Content-Type: application/json" \
  -d '{
    "duration_days": 7,
    "points": 200,
    "discount_percent": 20,
    "minimum_spend": 100
  }'
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND WEBSITE                        │
│  (React / Vue / Angular / HTML+JavaScript)                  │
└────────────┬────────────────────────────────────────────────┘
             │
             │ HTTP/REST API Calls
             │ (JSON Request/Response)
             ▼
┌─────────────────────────────────────────────────────────────┐
│              FLASK REST API SERVER (app.py)                  │
│  ┌──────────────────┐  ┌──────────────────────────────┐    │
│  │  Standard APIs   │  │   ML Prediction APIs         │    │
│  │  /api/*          │  │   /api/ml/*                  │    │
│  └────────┬─────────┘  └─────────┬────────────────────┘    │
│           │                       │                          │
│           ▼                       ▼                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         ML Prediction Service                        │   │
│  │  (ml_prediction_service.py)                         │   │
│  │  - Demand Forecaster                                │   │
│  │  - Campaign Predictor (✅ Already Trained!)        │   │
│  │  - Customer Churn Scorer                            │   │
│  │  - Cashier Risk Monitor                             │   │
│  └─────────────────────┬───────────────────────────────┘   │
└────────────────────────┼───────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         SQLite DATABASE (fresh_flow_markets.db)              │
│  - fct_orders, fct_order_items                              │
│  - fct_campaigns                                            │
│  - dim_items, dim_users, dim_places                         │
│  - fct_cash_balances                                        │
└─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│         TRAINED ML MODELS (models/*.pkl)                     │
│  - campaign_redemption_regressor.pkl ✅                     │
│  - campaign_success_classifier.pkl ✅                       │
│  - demand_forecaster.pkl (to be trained)                    │
│  - churn_classifier.pkl (to be trained)                     │
│  - cashier_risk_detector.pkl (to be trained)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Integration

### Option 1: React/Next.js Integration

#### Install Dependencies
```bash
npm install axios
# or
npm install fetch
```

#### Create API Client Service

```javascript
// services/freshFlowAPI.js
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';
const ML_BASE_URL = `${API_BASE_URL}/ml`;

class FreshFlowAPI {
  // ==================== ML PREDICTIONS ====================
  
  // Demand Forecasting
  async forecastDemand(itemId, forecastDays = 7) {
    const response = await axios.post(`${ML_BASE_URL}/forecast/demand`, {
      item_id: itemId,
      forecast_days: forecastDays
    });
    return response.data;
  }
  
  async getReorderRecommendations(itemId, currentStock) {
    const response = await axios.post(`${ML_BASE_URL}/forecast/reorder-recommendations`, {
      item_id: itemId,
      current_stock: currentStock
    });
    return response.data;
  }
  
  // Campaign Prediction
  async predictCampaign(campaignParams) {
    const response = await axios.post(`${ML_BASE_URL}/campaigns/predict`, campaignParams);
    return response.data;
  }
  
  async optimizeCampaign(targetRedemptions = 25, maxDiscount = 30) {
    const response = await axios.post(`${ML_BASE_URL}/campaigns/optimize`, {
      target_redemptions: targetRedemptions,
      max_discount: maxDiscount
    });
    return response.data;
  }
  
  async compareCampaigns(campaignScenarios) {
    const response = await axios.post(`${ML_BASE_URL}/campaigns/batch-predict`, {
      campaigns: campaignScenarios
    });
    return response.data;
  }
  
  // Customer Churn
  async predictChurnRisk(customerData) {
    const response = await axios.post(`${ML_BASE_URL}/customers/churn-risk`, customerData);
    return response.data;
  }
  
  async getHighRiskCustomers(customers) {
    const response = await axios.post(`${ML_BASE_URL}/customers/batch-churn-risk`, {
      customers
    });
    return response.data;
  }
  
  // Cashier Risk
  async detectCashierRisk(shiftData) {
    const response = await axios.post(`${ML_BASE_URL}/operations/cashier-risk`, shiftData);
    return response.data;
  }
  
  // ==================== STANDARD API ====================
  
  // Inventory
  async getInventoryItems(page = 1, perPage = 50, search = '') {
    const response = await axios.get(`${API_BASE_URL}/inventory/items`, {
      params: { page, per_page: perPage, search }
    });
    return response.data;
  }
  
  async getLowStockItems() {
    const response = await axios.get(`${API_BASE_URL}/inventory/low-stock`);
    return response.data;
  }
  
  // Orders
  async getOrders(page = 1, filters = {}) {
    const response = await axios.get(`${API_BASE_URL}/orders`, {
      params: { page, ...filters }
    });
    return response.data;
  }
  
  // Analytics
  async getDashboardStats(days = 30) {
    const response = await axios.get(`${API_BASE_URL}/analytics/dashboard`, {
      params: { days }
    });
    return response.data;
  }
  
  // Health Check
  async checkHealth() {
    const response = await axios.get(`${ML_BASE_URL}/health`);
    return response.data;
  }
  
  async getModelStatus() {
    const response = await axios.get(`${ML_BASE_URL}/models/status`);
    return response.data;
  }
}

export default new FreshFlowAPI();
```

#### React Component Examples

##### 1. Campaign Predictor Component

```jsx
// components/CampaignPredictor.jsx
import { useState } from 'react';
import api from '../services/freshFlowAPI';

export default function CampaignPredictor() {
  const [formData, setFormData] = useState({
    duration_days: 7,
    points: 200,
    discount_percent: 20,
    minimum_spend: 100
  });
  
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await api.predictCampaign(formData);
      
      if (result.success && result.data.status === 'success') {
        setPrediction(result.data);
      } else if (result.data.status === 'model_not_ready') {
        alert('Campaign model is still training. Please try again later.');
      }
    } catch (error) {
      console.error('Prediction failed:', error);
      alert('Failed to predict campaign performance');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="campaign-predictor">
      <h2>Campaign Performance Predictor</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Duration (days):</label>
          <input
            type="number"
            value={formData.duration_days}
            onChange={(e) => setFormData({...formData, duration_days: parseInt(e.target.value)})}
            min="1"
            max="30"
          />
        </div>
        
        <div className="form-group">
          <label>Points:</label>
          <input
            type="number"
            value={formData.points}
            onChange={(e) => setFormData({...formData, points: parseInt(e.target.value)})}
            min="0"
          />
        </div>
        
        <div className="form-group">
          <label>Discount (%):</label>
          <input
            type="number"
            value={formData.discount_percent}
            onChange={(e) => setFormData({...formData, discount_percent: parseFloat(e.target.value)})}
            min="0"
            max="100"
            step="0.1"
          />
        </div>
        
        <div className="form-group">
          <label>Minimum Spend (DKK):</label>
          <input
            type="number"
            value={formData.minimum_spend}
            onChange={(e) => setFormData({...formData, minimum_spend: parseFloat(e.target.value)})}
            min="0"
            step="0.01"
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Predicting...' : 'Predict Campaign Performance'}
        </button>
      </form>
      
      {prediction && (
        <div className={`prediction-result ${prediction.predictions.is_successful ? 'success' : 'warning'}`}>
          <h3>Prediction Results</h3>
          
          <div className="metrics">
            <div className="metric">
              <span className="label">Expected Redemptions:</span>
              <span className="value">{prediction.predictions.expected_redemptions}</span>
            </div>
            
            <div className="metric">
              <span className="label">Success Probability:</span>
              <span className="value">{prediction.predictions.success_probability}%</span>
            </div>
            
            <div className="metric">
              <span className="label">Recommendation:</span>
              <span className={`value recommendation-${prediction.recommendation.action.toLowerCase()}`}>
                {prediction.recommendation.action}
              </span>
            </div>
          </div>
          
          <div className="recommendation-box">
            <strong>Why:</strong> {prediction.recommendation.reason}
          </div>
        </div>
      )}
    </div>
  );
}
```

##### 2. Demand Forecast Dashboard

```jsx
// components/DemandForecastDashboard.jsx
import { useState, useEffect } from 'react';
import api from '../services/freshFlowAPI';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function DemandForecastDashboard() {
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    loadItems();
  }, []);
  
  const loadItems = async () => {
    const result = await api.getInventoryItems(1, 100);
    if (result.success) {
      setItems(result.data);
    }
  };
  
  const forecastItem = async (itemId) => {
    setLoading(true);
    try {
      const result = await api.forecastDemand(itemId, 7);
      
      if (result.success && result.data.status === 'success') {
        setForecast(result.data);
      }
    } catch (error) {
      console.error('Forecast failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const getRecommendations = async () => {
    if (!selectedItem) return;
    
    const result = await api.getReorderRecommendations(
      selectedItem.id,
      selectedItem.current_stock
    );
    
    if (result.success) {
      alert(`Reorder Recommendation:\nQuantity: ${result.data.recommendations.reorder_quantity}\nUrgency: ${result.data.recommendations.urgency}`);
    }
  };
  
  return (
    <div className="demand-forecast-dashboard">
      <h2>Demand Forecasting</h2>
      
      <div className="item-selector">
        <select onChange={(e) => {
          const item = items.find(i => i.id === parseInt(e.target.value));
          setSelectedItem(item);
          forecastItem(item.id);
        }}>
          <option value="">Select an item...</option>
          {items.map(item => (
            <option key={item.id} value={item.id}>
              {item.title} (Stock: {item.current_stock})
            </option>
          ))}
        </select>
        
        {selectedItem && (
          <button onClick={getRecommendations}>
            Get Reorder Recommendations
          </button>
        )}
      </div>
      
      {loading && <div className="loader">Loading forecast...</div>}
      
      {forecast && !loading && (
        <div className="forecast-results">
          <div className="summary-cards">
            <div className="card">
              <h4>Total Predicted Demand</h4>
              <div className="value">{forecast.summary.total_predicted_demand}</div>
            </div>
            
            <div className="card">
              <h4>Avg Daily Demand</h4>
              <div className="value">{forecast.summary.avg_daily_demand}</div>
            </div>
            
            <div className="card">
              <h4>Peak Day</h4>
              <div className="value">{forecast.summary.peak_day.day_of_week}</div>
              <div className="sub-value">{forecast.summary.peak_day.predicted_quantity} units</div>
            </div>
          </div>
          
          <div className="chart-container">
            <h3>7-Day Demand Forecast</h3>
            <LineChart width={600} height={300} data={forecast.predictions}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day_of_week" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="predicted_quantity" 
                stroke="#8884d8" 
                name="Predicted Demand"
              />
            </LineChart>
          </div>
        </div>
      )}
    </div>
  );
}
```

##### 3. Customer Churn Risk Monitor

```jsx
// components/ChurnRiskMonitor.jsx
import { useState, useEffect } from 'react';
import api from '../services/freshFlowAPI';

export default function ChurnRiskMonitor() {
  const [highRiskCustomers, setHighRiskCustomers] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const loadHighRiskCustomers = async () => {
    setLoading(true);
    
    // In real implementation, fetch customer data from database
    // For now, using sample data
    const sampleCustomers = [
      {
        customer_id: 123,
        recent_waiting_time: 35,
        recent_rating: 2.5,
        points_redeemed: 150,
        vip_threshold: 1000,
        days_since_last_order: 25
      }
    ];
    
    try {
      const result = await api.getHighRiskCustomers(sampleCustomers);
      
      if (result.success) {
        setHighRiskCustomers(result.high_risk_customers || []);
      }
    } catch (error) {
      console.error('Failed to load churn risks:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadHighRiskCustomers();
  }, []);
  
  return (
    <div className="churn-risk-monitor">
      <h2>Customer Churn Risk Monitor</h2>
      
      <div className="summary">
        <span className="count-badge critical">
          {highRiskCustomers.length} High-Risk Customers
        </span>
      </div>
      
      {loading && <div className="loader">Loading...</div>}
      
      <div className="customer-list">
        {highRiskCustomers.map((customer, idx) => (
          <div key={idx} className={`customer-card risk-${customer.churn_risk.level}`}>
            <div className="customer-header">
              <h3>Customer #{customer.customer_id}</h3>
              <span className="risk-badge">
                {customer.churn_risk.probability}% Churn Risk
              </span>
            </div>
            
            <div className="customer-insights">
              <div className="insight">
                <span className="label">Engagement:</span>
                <span className="value">{customer.customer_insights.engagement_level}</span>
              </div>
              
              <div className="insight">
                <span className="label">Satisfaction:</span>
                <span className="value">{customer.customer_insights.satisfaction_score}</span>
              </div>
            </div>
            
            <div className="retention-actions">
              <h4>Recommended Actions:</h4>
              <ul>
                {customer.retention_strategy.recommended_actions.map((action, i) => (
                  <li key={i}>{action}</li>
                ))}
              </ul>
              
              <div className="action-cost">
                Estimated Cost: {customer.retention_strategy.estimated_retention_cost} DKK
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### Option 2: Vue.js Integration

```vue
<!-- components/CampaignPredictor.vue -->
<template>
  <div class="campaign-predictor">
    <h2>Campaign Performance Predictor</h2>
    
    <form @submit.prevent="predictCampaign">
      <div class="form-group">
        <label>Duration (days):</label>
        <input v-model.number="campaign.duration_days" type="number" min="1" />
      </div>
      
      <div class="form-group">
        <label>Points:</label>
        <input v-model.number="campaign.points" type="number" min="0" />
      </div>
      
      <div class="form-group">
        <label>Discount (%):</label>
        <input v-model.number="campaign.discount_percent" type="number" min="0" max="100" step="0.1" />
      </div>
      
      <div class="form-group">
        <label>Minimum Spend (DKK):</label>
        <input v-model.number="campaign.minimum_spend" type="number" min="0" step="0.01" />
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? 'Predicting...' : 'Predict Performance' }}
      </button>
    </form>
    
    <div v-if="prediction" class="prediction-result">
      <h3>Results</h3>
      <p>Expected Redemptions: <strong>{{ prediction.predictions.expected_redemptions }}</strong></p>
      <p>Success Probability: <strong>{{ prediction.predictions.success_probability }}%</strong></p>
      <p>Recommendation: <strong>{{ prediction.recommendation.action }}</strong></p>
      <p class="reason">{{ prediction.recommendation.reason }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      campaign: {
        duration_days: 7,
        points: 200,
        discount_percent: 20,
        minimum_spend: 100
      },
      prediction: null,
      loading: false
    }
  },
  
  methods: {
    async predictCampaign() {
      this.loading = true;
      
      try {
        const response = await axios.post(
          'http://localhost:5000/api/ml/campaigns/predict',
          this.campaign
        );
        
        if (response.data.success) {
          this.prediction = response.data.data;
        }
      } catch (error) {
        console.error('Prediction failed:', error);
        alert('Failed to predict campaign');
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
```

---

### Option 3: Vanilla JavaScript / HTML

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fresh Flow Markets - Campaign Predictor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:disabled {
            background: #ccc;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 4px;
        }
        .success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
        }
    </style>
</head>
<body>
    <h1>Campaign Performance Predictor</h1>
    
    <form id="campaignForm">
        <div class="form-group">
            <label for="duration">Duration (days):</label>
            <input type="number" id="duration" value="7" min="1" required>
        </div>
        
        <div class="form-group">
            <label for="points">Points:</label>
            <input type="number" id="points" value="200" min="0" required>
        </div>
        
        <div class="form-group">
            <label for="discount">Discount (%):</label>
            <input type="number" id="discount" value="20" min="0" max="100" step="0.1" required>
        </div>
        
        <div class="form-group">
            <label for="minSpend">Minimum Spend (DKK):</label>
            <input type="number" id="minSpend" value="100" min="0" step="0.01" required>
        </div>
        
        <button type="submit" id="predictBtn">Predict Campaign</button>
    </form>
    
    <div id="result" style="display: none;"></div>
    
    <script>
        const API_URL = 'http://localhost:5000/api/ml';
        
        document.getElementById('campaignForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const button = document.getElementById('predictBtn');
            button.disabled = true;
            button.textContent = 'Predicting...';
            
            const campaignData = {
                duration_days: parseInt(document.getElementById('duration').value),
                points: parseInt(document.getElementById('points').value),
                discount_percent: parseFloat(document.getElementById('discount').value),
                minimum_spend: parseFloat(document.getElementById('minSpend').value)
            };
            
            try {
                const response = await fetch(`${API_URL}/campaigns/predict`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(campaignData)
                });
                
                const data = await response.json();
                
                if (data.success && data.data.status === 'success') {
                    const prediction = data.data;
                    const resultDiv = document.getElementById('result');
                    
                    resultDiv.innerHTML = `
                        <h2>Prediction Results</h2>
                        <p><strong>Expected Redemptions:</strong> ${prediction.predictions.expected_redemptions}</p>
                        <p><strong>Success Probability:</strong> ${prediction.predictions.success_probability}%</p>
                        <p><strong>Recommendation:</strong> ${prediction.recommendation.action}</p>
                        <p><em>${prediction.recommendation.reason}</em></p>
                    `;
                    
                    resultDiv.className = prediction.predictions.is_successful ? 'result success' : 'result';
                    resultDiv.style.display = 'block';
                } else {
                    alert('Model not ready or prediction failed');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to connect to API');
            } finally {
                button.disabled = false;
                button.textContent = 'Predict Campaign';
            }
        });
    </script>
</body>
</html>
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] **API Configuration**
  - [ ] Set production database path
  - [ ] Configure CORS for production domain
  - [ ] Set up API key authentication
  - [ ] Enable rate limiting
  
- [ ] **Database**
  - [ ] Run database readiness checks (see ML_DATABASE_READINESS.md)
  - [ ] Add missing fields if needed (rating, waiting_time)
  - [ ] Create performance indexes
  - [ ] Set up database backups
  
- [ ] **ML Models**
  - [ ] Campaign ROI model ✅ (already trained)
  - [ ] Train Demand Forecaster model
  - [ ] Train Customer Churn model
  - [ ] Train Cashier Risk model
  - [ ] Test all models with sample data

### Production Deployment

#### Option 1: Traditional Server (Linux)

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# Set up application
cd /var/www/fresh-flow-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure gunicorn
pip install gunicorn

# Run with gunicorn (production WSGI server)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Set up systemd service for auto-restart
sudo nano /etc/systemd/system/freshflow-api.service
```

`freshflow-api.service`:
```ini
[Unit]
Description=Fresh Flow Markets API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/fresh-flow-api
Environment="PATH=/var/www/fresh-flow-api/venv/bin"
ExecStart=/var/www/fresh-flow-api/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start freshflow-api
sudo systemctl enable freshflow-api

# Configure nginx as reverse proxy
sudo nano /etc/nginx/sites-available/freshflow-api
```

#### Option 2: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./fresh_flow_markets.db:/app/fresh_flow_markets.db
      - ./models:/app/models
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

Deploy:
```bash
docker-compose up -d
```

#### Option 3: Cloud Deployment (Heroku/AWS/Azure)

See `docs/CLOUD_BACKEND_GUIDE.md` for detailed instructions.

---

## Security Recommendations

### 1. Add API Key Authentication

```python
# src/api/middleware.py
from functools import wraps
from flask import request, jsonify
import os

API_KEYS = set(os.getenv('API_KEYS', '').split(','))

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key or api_key not in API_KEYS:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Usage in routes:
@ml_bp.route('/campaigns/predict', methods=['POST'])
@require_api_key
def predict_campaign():
    ...
```

### 2. Rate Limiting

```python
# Install: pip install Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@ml_bp.route('/campaigns/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict_campaign():
    ...
```

### 3. HTTPS Only (Production)

Configure your web server (nginx/Apache) to redirect HTTP to HTTPS.

---

## Monitoring & Logging

### Add Request Logging

```python
# src/api/__init__.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")
```

---

## Troubleshooting

### Common Issues

#### 1. CORS Error in Browser
```
Access to fetch at 'http://localhost:5000/api/ml/...' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Solution**: Verify CORS is configured correctly in `src/api/__init__.py`. The current setup allows all origins (`*`). For production, specify your domain:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        ...
    }
})
```

#### 2. Model Not Ready Error
```json
{
  "status": "model_not_ready",
  "message": "Demand forecasting model not yet trained"
}
```

**Solution**: The model hasn't been trained yet. Only Campaign ROI model is currently trained. Train other models using the notebooks in `ML_Models/`.

#### 3. Database Not Found
```
sqlite3.OperationalError: unable to open database file
```

**Solution**: Ensure `fresh_flow_markets.db` exists in the project root. Run `python database/setup_database.py` if needed.

---

## Support Resources

- **API Documentation**: `/docs/ML_API_DOCUMENTATION.md`
- **Database Schema**: `/database/DATABASE_SCHEMA.md`
- **Database Readiness**: `/database/ML_DATABASE_READINESS.md`
- **Campaign Model README**: `/ML_Models/Campaign_ROI_Predictor/README.md`

---

## Next Steps

1. ✅ **Test the API** - Use provided examples to test endpoints
2. ⏳ **Train Remaining Models** - Complete Demand, Churn, and Cashier models
3. ✅ **Build Frontend** - Use React/Vue examples as templates
4. ⏳ **Deploy to Production** - Follow deployment checklist
5. ⏳ **Monitor & Optimize** - Set up logging and performance monitoring

**API Status**: ✅ READY FOR INTEGRATION

The infrastructure is ready. Start building your frontend dashboard!
