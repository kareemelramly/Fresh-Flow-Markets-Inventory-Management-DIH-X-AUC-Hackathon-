import requests
import json

API_BASE = "http://localhost:5000"

# Test 1: Normal forecast (no campaign, no holiday)
print("=" * 60)
print("TEST 1: Normal Forecast (No Campaign, No Holiday)")
print("=" * 60)
response = requests.post(f"{API_BASE}/api/ml/forecast/demand", json={
    "item_id": 59856,
    "forecast_days": 7,
    "is_holiday": False,
    "campaign_active": False
})
data = response.json()['data']
for pred in data['predictions']:
    print(f"  {pred['date']} ({pred['day_of_week']:9s}): {pred['predicted_quantity']:6.2f} units")
total = sum(p['predicted_quantity'] for p in data['predictions'])
print(f"  TOTAL: {total:.2f} units\n")

# Test 2: With campaign active
print("=" * 60)
print("TEST 2: With Campaign Active")
print("=" * 60)
response = requests.post(f"{API_BASE}/api/ml/forecast/demand", json={
    "item_id": 59856,
    "forecast_days": 7,
    "is_holiday": False,
    "campaign_active": True
})
data = response.json()['data']
for pred in data['predictions']:
    print(f"  {pred['date']} ({pred['day_of_week']:9s}): {pred['predicted_quantity']:6.2f} units")
total = sum(p['predicted_quantity'] for p in data['predictions'])
print(f"  TOTAL: {total:.2f} units\n")

# Test 3: With holiday
print("=" * 60)
print("TEST 3: With Holiday")
print("=" * 60)
response = requests.post(f"{API_BASE}/api/ml/forecast/demand", json={
    "item_id": 59856,
    "forecast_days": 7,
    "is_holiday": True,
    "campaign_active": False
})
data = response.json()['data']
for pred in data['predictions']:
    print(f"  {pred['date']} ({pred['day_of_week']:9s}): {pred['predicted_quantity']:6.2f} units")
total = sum(p['predicted_quantity'] for p in data['predictions'])
print(f"  TOTAL: {total:.2f} units\n")

# Test 4: Campaign + Holiday (maximum boost)
print("=" * 60)
print("TEST 4: Campaign + Holiday (Maximum Boost)")
print("=" * 60)
response = requests.post(f"{API_BASE}/api/ml/forecast/demand", json={
    "item_id": 59856,
    "forecast_days": 7,
    "is_holiday": True,
    "campaign_active": True
})
data = response.json()['data']
for pred in data['predictions']:
    print(f"  {pred['date']} ({pred['day_of_week']:9s}): {pred['predicted_quantity']:6.2f} units")
total = sum(p['predicted_quantity'] for p in data['predictions'])
print(f"  TOTAL: {total:.2f} units\n")

print("=" * 60)
print("SUMMARY")
print("=" * 60)
print("Multipliers:")
print("  Base:                    1.0x")
print("  Weekend:                 1.5x")
print("  Holiday:                 1.3x")
print("  Campaign:                1.4x")
print("  Weekend + Holiday + Campaign: 2.73x (1.5 * 1.3 * 1.4)")
