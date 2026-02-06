# Fresh Flow Markets - ML Prediction API Documentation

## Overview

This API provides machine learning predictions for Fresh Flow Markets, supporting:
1. **Demand & Stock Forecasting** - Predict item demand and get reorder recommendations
2. **Campaign ROI & Redemption Prediction** - Predict campaign success before launch
3. **Customer Churn & Loyalty Scoring** - Identify at-risk customers
4. **Operational Risk Monitoring** - Detect cashier anomalies and integrity issues

**Base URL**: `http://localhost:5000/api/ml`

**Production URL**: `https://your-domain.com/api/ml`

## Authentication

Currently, the API does not require authentication. For production deployment, implement:
- API Key authentication via `X-API-Key` header
- JWT tokens for user-specific requests
- Rate limiting per IP/API key

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": { /* model-specific response */ }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message description",
  "traceback": "Detailed error trace (development only)"
}
```

---

## 1. Demand & Stock Forecasting

### **POST** `/forecast/demand`

Predict demand for a specific item over the next N days.

#### Request Body
```json
{
  "item_id": 123,
  "forecast_days": 7,
  "is_holiday": false,
  "is_weekend": false,
  "campaign_active": false,
  "price": 99.99
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `item_id` | integer | ✅ | Item ID from dim_items table |
| `forecast_days` | integer | ❌ | Days to forecast (default: 7) |
| `is_holiday` | boolean | ❌ | Whether forecast includes holidays |
| `is_weekend` | boolean | ❌ | Whether forecast includes weekends |
| `campaign_active` | boolean | ❌ | Whether a campaign will be running |
| `price` | float | ❌ | Item price (uses current if omitted) |

#### Response
```json
{
  "success": true,
  "data": {
    "status": "success",
    "item_id": 123,
    "forecast_days": 7,
    "predictions": [
      {
        "date": "2026-02-06",
        "predicted_quantity": 45.5,
        "day_of_week": "Thursday",
        "is_weekend": false
      }
    ],
    "summary": {
      "total_predicted_demand": 318.5,
      "avg_daily_demand": 45.5,
      "peak_day": {
        "date": "2026-02-08",
        "predicted_quantity": 67.2,
        "day_of_week": "Saturday",
        "is_weekend": true
      }
    },
    "item_details": {
      "id": 123,
      "name": "Classic Burger",
      "current_price": 99.99,
      "current_stock": 50,
      "minimum_stock": 20
    }
  }
}
```

#### Example cURL
```bash
curl -X POST http://localhost:5000/api/ml/forecast/demand \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 123,
    "forecast_days": 7,
    "campaign_active": true
  }'
```

#### Example JavaScript (Fetch API)
```javascript
const response = await fetch('http://localhost:5000/api/ml/forecast/demand', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    item_id: 123,
    forecast_days: 7,
    campaign_active: true
  })
});

const data = await response.json();
if (data.success) {
  console.log('Total demand:', data.data.summary.total_predicted_demand);
}
```

---

### **POST** `/forecast/reorder-recommendations`

Get intelligent stock reorder recommendations based on demand forecast.

#### Request Body
```json
{
  "item_id": 123,
  "current_stock": 50.5,
  "lead_time_days": 3,
  "safety_stock_multiplier": 1.2
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `item_id` | integer | ✅ | Item ID |
| `current_stock` | float | ❌ | Current stock (uses DB if omitted) |
| `lead_time_days` | integer | ❌ | Supplier delivery time (default: 3) |
| `safety_stock_multiplier` | float | ❌ | Safety buffer (default: 1.2 = 20%) |

#### Response
```json
{
  "success": true,
  "data": {
    "status": "success",
    "item_id": 123,
    "current_stock": 50.5,
    "forecast_period_days": 10,
    "predicted_demand": 455.0,
    "recommendations": {
      "reorder_needed": true,
      "reorder_quantity": 495.5,
      "urgency": "high",
      "days_until_stockout": "2026-02-07",
      "safety_stock_level": 546.0
    }
  }
}
```

#### Urgency Levels
- `high` - Stockout expected within 3 days
- `medium` - Reorder needed but not urgent
- `low` - Stock levels adequate

---

### **POST** `/forecast/bulk-items`

Get forecasts for multiple items simultaneously (for dashboard views).

#### Request Body
```json
{
  "item_ids": [123, 456, 789],
  "forecast_days": 7
}
```

#### Response
```json
{
  "success": true,
  "total_items": 3,
  "forecasts": [
    {
      "status": "success",
      "item_id": 123,
      "summary": { /* forecast data */ }
    }
  ]
}
```

---

## 2. Campaign ROI & Redemption Prediction

### **POST** `/campaigns/predict`

Predict campaign performance before launching.

#### Request Body
```json
{
  "duration_days": 7,
  "points": 200,
  "discount_percent": 20,
  "minimum_spend": 100
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `duration_days` | integer | ✅ | Campaign duration (days) |
| `points` | integer | ✅ | Loyalty points offered |
| `discount_percent` | float | ✅ | Discount percentage (0-100) |
| `minimum_spend` | float | ✅ | Minimum spend requirement (DKK) |

#### Response
```json
{
  "success": true,
  "data": {
    "status": "success",
    "predictions": {
      "expected_redemptions": 22.0,
      "success_probability": 76.5,
      "is_successful": true
    },
    "campaign_details": {
      "duration_days": 7,
      "points": 200,
      "discount_percent": 20,
      "minimum_spend": 100
    },
    "recommendation": {
      "action": "LAUNCH",
      "reason": "High success probability with good redemption rate",
      "confidence": "high"
    }
  }
}
```

#### Recommendation Actions
- `LAUNCH` - High confidence, good metrics
- `LAUNCH WITH MONITORING` - Moderate success expected
- `TEST SMALL SCALE` - Uncertain outcome
- `REVISE` - Low success probability

#### Example React Component
```jsx
function CampaignPredictor() {
  const [prediction, setPrediction] = useState(null);
  
  const predictCampaign = async (params) => {
    const res = await fetch('http://localhost:5000/api/ml/campaigns/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    
    const data = await res.json();
    if (data.success) {
      setPrediction(data.data);
    }
  };
  
  return (
    <div>
      {prediction && (
        <div className={`alert alert-${
          prediction.predictions.success_probability > 70 ? 'success' : 'warning'
        }`}>
          <h3>Success Probability: {prediction.predictions.success_probability}%</h3>
          <p>Expected Redemptions: {prediction.predictions.expected_redemptions}</p>
          <p>Recommendation: {prediction.recommendation.action}</p>
        </div>
      )}
    </div>
  );
}
```

---

### **POST** `/campaigns/optimize`

Find optimal campaign parameters to achieve target goals.

#### Request Body
```json
{
  "target_redemptions": 25,
  "max_discount": 30,
  "budget_per_redemption": 100
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "status": "success",
    "optimal_parameters": {
      "duration_days": 7,
      "points": 200,
      "discount_percent": 20,
      "minimum_spend": 100,
      "expected_redemptions": 24.5,
      "success_probability": 82.3
    },
    "target_redemptions": 25,
    "optimization_score": 0.943
  }
}
```

---

### **POST** `/campaigns/batch-predict`

Compare multiple campaign scenarios to select the best option.

#### Request Body
```json
{
  "campaigns": [
    {
      "duration_days": 3,
      "points": 100,
      "discount_percent": 10,
      "minimum_spend": 50
    },
    {
      "duration_days": 7,
      "points": 200,
      "discount_percent": 20,
      "minimum_spend": 100
    }
  ]
}
```

#### Response
```json
{
  "success": true,
  "total_campaigns": 2,
  "predictions": [ /* array of predictions */ ],
  "best_campaign": {
    "campaign_index": 1,
    "predictions": {
      "success_probability": 82.3
    }
  }
}
```

---

## 3. Customer Churn & Loyalty Prediction

### **POST** `/customers/churn-risk`

Predict individual customer churn risk and get retention recommendations.

#### Request Body
```json
{
  "customer_id": 123,
  "recent_waiting_time": 25.5,
  "recent_rating": 3.5,
  "points_redeemed": 500,
  "vip_threshold": 1000,
  "days_since_last_order": 15
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `customer_id` | integer | ✅ | Customer ID |
| `recent_waiting_time` | float | ✅ | Avg waiting time (minutes) |
| `recent_rating` | float | ✅ | Recent order rating (1-5) |
| `points_redeemed` | integer | ✅ | Total points redeemed |
| `vip_threshold` | float | ✅ | VIP threshold points |
| `days_since_last_order` | integer | ✅ | Days since last order |

#### Response
```json
{
  "success": true,
  "data": {
    "status": "success",
    "customer_id": 123,
    "churn_risk": {
      "probability": 68.5,
      "level": "high",
      "will_churn": true
    },
    "retention_strategy": {
      "urgency": "high",
      "recommended_actions": [
        "Send personalized email with 15% discount",
        "Bonus points reward on next order",
        "Request feedback survey with incentive"
      ],
      "estimated_retention_cost": 25
    },
    "customer_insights": {
      "satisfaction_score": 0.95,
      "engagement_level": "medium",
      "is_vip": false
    }
  }
}
```

#### Risk Levels
- `critical` (≥70%) - Immediate intervention required
- `high` (40-69%) - Proactive retention strategy needed
- `low` (<40%) - Standard engagement sufficient

---

### **POST** `/customers/batch-churn-risk`

Identify high-risk customers across your entire customer base.

#### Request Body
```json
{
  "customers": [
    {
      "customer_id": 123,
      "recent_waiting_time": 25.5,
      "recent_rating": 3.5,
      "points_redeemed": 500,
      "vip_threshold": 1000,
      "days_since_last_order": 15
    }
  ]
}
```

#### Response
```json
{
  "success": true,
  "total_customers": 100,
  "predictions": [ /* all predictions */ ],
  "high_risk_count": 15,
  "high_risk_customers": [
    {
      "customer_id": 456,
      "churn_risk": {
        "probability": 85.2,
        "level": "critical"
      }
    }
  ]
}
```

---

## 4. Operational Risk & Cashier Integrity

### **POST** `/operations/cashier-risk`

Detect anomalous cashier behavior or operational risks.

#### Request Body
```json
{
  "cashier_id": 45,
  "shift_date": "2026-02-05",
  "order_count": 150,
  "expected_balance": 15000.00,
  "actual_balance": 14850.00,
  "total_vat": 3000.00,
  "avg_order_value": 100.00
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cashier_id` | integer | ✅ | Cashier/user ID |
| `shift_date` | string | ✅ | Shift date (YYYY-MM-DD) |
| `order_count` | integer | ✅ | Orders processed |
| `expected_balance` | float | ✅ | Expected cash balance |
| `actual_balance` | float | ✅ | Actual cash balance |
| `total_vat` | float | ✅ | Total VAT collected |
| `avg_order_value` | float | ❌ | Average order value |

#### Response
```json
{
  "success": true,
  "data": {
    "status": "success",
    "cashier_id": 45,
    "shift_date": "2026-02-05",
    "risk_assessment": {
      "risk_score": 0.234,
      "risk_level": "low",
      "alert_type": "normal_operations",
      "requires_action": false
    },
    "financial_metrics": {
      "expected_balance": 15000.00,
      "actual_balance": 14850.00,
      "difference": 150.00,
      "discrepancy_percent": 1.0,
      "total_vat": 3000.00
    },
    "operational_metrics": {
      "order_count": 150,
      "avg_order_value": 100.00,
      "orders_per_hour": 18.75
    },
    "recommended_actions": [
      "No action required"
    ]
  }
}
```

#### Risk Levels
- `critical` (≥0.8) - Immediate investigation required
- `high` (0.5-0.79) - Flagged for manager review
- `medium` (0.3-0.49) - Monitoring needed
- `low` (<0.3) - Normal operations

---

### **POST** `/operations/batch-cashier-risk`

Monitor multiple shifts for anomalies simultaneously.

#### Request Body
```json
{
  "shifts": [
    {
      "cashier_id": 45,
      "shift_date": "2026-02-05",
      "order_count": 150,
      "expected_balance": 15000.00,
      "actual_balance": 14850.00,
      "total_vat": 3000.00
    }
  ]
}
```

#### Response
```json
{
  "success": true,
  "total_shifts": 10,
  "detections": [ /* all shift analyses */ ],
  "critical_risk_count": 2,
  "critical_risks": [
    {
      "cashier_id": 47,
      "shift_date": "2026-02-05",
      "risk_assessment": {
        "risk_score": 0.892,
        "risk_level": "critical"
      }
    }
  ]
}
```

---

## Utility Endpoints

### **GET** `/health`

Check ML service health status.

#### Response
```json
{
  "service": "ML Prediction Service",
  "status": "healthy",
  "models_available": {
    "demand_forecast": true,
    "campaign_roi": true,
    "customer_churn": false,
    "cashier_risk": false
  },
  "total_models": 4,
  "ready_models": 2,
  "models_directory": "models"
}
```

---

### **GET** `/models/status`

Get detailed status of all ML models.

#### Response
```json
{
  "success": true,
  "models": {
    "demand_forecast": {
      "available": false,
      "name": "Dynamic Demand & Stock Forecaster",
      "type": "Regression/Time-Series",
      "description": "Predicts item demand to prevent low stock situations"
    },
    "campaign_roi": {
      "available": true,
      "name": "Campaign ROI & Redemption Predictor",
      "type": "Classification/Regression",
      "description": "Predicts campaign success probability and redemption frequency"
    }
  }
}
```

---

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (missing/invalid parameters)
- `404` - Resource Not Found
- `500` - Server Error

### Model Not Ready Response
When a model hasn't been trained yet:
```json
{
  "success": true,
  "data": {
    "status": "model_not_ready",
    "message": "Demand forecasting model not yet trained"
  }
}
```

---

## Rate Limiting (Production Recommendation)

Implement rate limiting for production:
```
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Batch endpoints: 50 requests/hour
```

---

## CORS Configuration

The API supports Cross-Origin Resource Sharing (CORS) with:
- **Allowed Origins**: `*` (all origins - restrict in production)
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Content-Type, Authorization
- **Max Age**: 3600 seconds

---

## Integration Examples

### React Dashboard Example
```jsx
import { useState, useEffect } from 'react';

function MLDashboard() {
  const [modelStatus, setModelStatus] = useState(null);
  const API_BASE = 'http://localhost:5000/api/ml';
  
  useEffect(() => {
    // Check which models are available
    fetch(`${API_BASE}/models/status`)
      .then(res => res.json())
      .then(data => setModelStatus(data.models));
  }, []);
  
  const forecastDemand = async (itemId) => {
    const response = await fetch(`${API_BASE}/forecast/demand`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        item_id: itemId,
        forecast_days: 7
      })
    });
    
    return await response.json();
  };
  
  return (
    <div>
      <h1>ML Predictions Dashboard</h1>
      {modelStatus && (
        <div>
          {Object.entries(modelStatus).map(([key, model]) => (
            <div key={key} className={model.available ? 'available' : 'unavailable'}>
              <h3>{model.name}</h3>
              <p>{model.description}</p>
              <span>{model.available ? '✅ Ready' : '⏳ Training'}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Vue.js Integration
```vue
<template>
  <div>
    <button @click="predictCampaign">Predict Campaign</button>
    <div v-if="prediction">
      Success Rate: {{ prediction.predictions.success_probability }}%
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      prediction: null
    }
  },
  methods: {
    async predictCampaign() {
      const response = await fetch('http://localhost:5000/api/ml/campaigns/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          duration_days: 7,
          points: 200,
          discount_percent: 20,
          minimum_spend: 100
        })
      });
      
      const data = await response.json();
      if (data.success) {
        this.prediction = data.data;
      }
    }
  }
}
</script>
```

### Python Client
```python
import requests

class FreshFlowMLClient:
    def __init__(self, base_url='http://localhost:5000/api/ml'):
        self.base_url = base_url
    
    def predict_demand(self, item_id, forecast_days=7):
        response = requests.post(
            f'{self.base_url}/forecast/demand',
            json={'item_id': item_id, 'forecast_days': forecast_days}
        )
        return response.json()
    
    def predict_campaign(self, duration_days, points, discount_percent, minimum_spend):
        response = requests.post(
            f'{self.base_url}/campaigns/predict',
            json={
                'duration_days': duration_days,
                'points': points,
                'discount_percent': discount_percent,
                'minimum_spend': minimum_spend
            }
        )
        return response.json()

# Usage
client = FreshFlowMLClient()
result = client.predict_demand(item_id=123, forecast_days=7)
print(f"Total demand: {result['data']['summary']['total_predicted_demand']}")
```

---

## Support & Contact

For API support, contact: **dev@freshflowmarkets.com**

**Documentation Version**: 2.0  
**Last Updated**: February 5, 2026
