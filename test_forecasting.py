import requests
import json

API_BASE = "http://localhost:5000"

print("="*80)
print("TESTING FORECASTING ENDPOINTS")
print("="*80)

# Test 1: Demand Forecast
print("\n1. Testing Demand Forecast...")
response = requests.post(
    f"{API_BASE}/api/ml/forecast/demand",
    json={
        "item_id": 59837,
        "forecast_days": 7,
        "is_holiday": False,
        "is_weekend": False,
        "campaign_active": False
    },
    timeout=30
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        forecast = data['data']
        print(f"✅ Forecast generated successfully")
        print(f"   Status: {forecast.get('status')}")
        print(f"   Predicted Demand: {forecast.get('predicted_demand', 0):.1f} units")
        print(f"   Confidence: {forecast.get('confidence', 0):.0%}")
    else:
        print(f"❌ Error: {data.get('error')}")
else:
    print(f"❌ HTTP Error: {response.status_code}")
    print(f"   Response: {response.text[:200]}")

# Test 2: Reorder Recommendations
print("\n2. Testing Reorder Recommendations...")
response = requests.post(
    f"{API_BASE}/api/ml/forecast/reorder-recommendations",
    json={
        "item_id": 59837,
        "current_stock": 100,
        "lead_time_days": 3,
        "safety_stock_multiplier": 1.2
    },
    timeout=30
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        reorder = data['data']
        print(f"✅ Reorder recommendation generated")
        print(f"   Reorder Quantity: {reorder.get('reorder_quantity', 0):.0f} units")
        print(f"   Safety Stock: {reorder.get('safety_stock', 0):.0f} units")
        print(f"   Should Reorder: {'Yes' if reorder.get('should_reorder') else 'No'}")
    else:
        print(f"❌ Error: {data.get('error')}")
else:
    print(f"❌ HTTP Error: {response.status_code}")
    print(f"   Response: {response.text[:200]}")

# Test 3: Bulk Forecast
print("\n3. Testing Bulk Forecast...")
response = requests.post(
    f"{API_BASE}/api/ml/forecast/bulk-items",
    json={
        "item_ids": [59837, 59838, 59839],
        "forecast_days": 7
    },
    timeout=60
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print(f"✅ Bulk forecast generated")
        print(f"   Total items: {data.get('total_items')}")
        forecasts = data.get('forecasts', [])
        success_count = sum(1 for f in forecasts if f.get('status') == 'success')
        print(f"   Successful: {success_count}/{len(forecasts)}")
    else:
        print(f"❌ Error: {data.get('error')}")
else:
    print(f"❌ HTTP Error: {response.status_code}")
    print(f"   Response: {response.text[:200]}")

print("\n" + "="*80)
print("FORECASTING API TEST COMPLETE")
print("="*80)
