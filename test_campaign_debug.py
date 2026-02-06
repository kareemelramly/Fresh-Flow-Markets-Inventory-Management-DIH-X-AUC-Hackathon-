"""Debug Campaign ML endpoint"""
import requests
import json

API_URL = "http://localhost:5000"

print("="*80)
print("DEBUGGING CAMPAIGN ML ENDPOINT")
print("="*80)

# Test Campaign Prediction
print("\n1. Testing Campaign Prediction Endpoint...")
try:
    response = requests.post(
        f"{API_URL}/api/ml/campaigns/predict",
        json={
            "duration_days": 30,
            "points": 50,
            "discount_percent": 10,
            "minimum_spend": 100
        },
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"ERROR: {e}")

# Test Model Status
print("\n2. Testing Model Status...")
try:
    response = requests.get(f"{API_URL}/api/ml/models/status", timeout=5)
    data = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"\nCampaign ROI Model:")
    print(f"  Trained: {data.get('campaign_roi', {}).get('trained', False)}")
    print(f"  Ready: {data.get('campaign_roi', {}).get('ready', False)}")
    print(f"  Message: {data.get('campaign_roi', {}).get('message', 'N/A')}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*80)
