"""Quick API test - 30 seconds"""
import requests
import time
import sys

API_URL = "http://localhost:5000"

print("="*80, flush=True)
print("QUICK API TEST (30 seconds)", flush=True)
print("="*80, flush=True)
print(f"\nTesting: {API_URL}\n", flush=True)

tests = []

# 1. Health
try:
    r = requests.get(f"{API_URL}/health", timeout=3)
    tests.append(("✅ Health", r.status_code == 200))
except: tests.append(("❌ Health", False))

# 2. ML Health  
try:
    r = requests.get(f"{API_URL}/api/ml/health", timeout=3)
    tests.append(("✅ ML Health", r.status_code == 200))
except: tests.append(("❌ ML Health", False))

# 3. ML Models Status
try:
    r = requests.get(f"{API_URL}/api/ml/models/status", timeout=3)
    data = r.json()
    tests.append(("✅ ML Models", r.status_code == 200))
    print(f"   Campaign ROI: {data.get('campaign_roi', {}).get('trained', False)}", flush=True)
except: tests.append(("❌ ML Models", False))

# 4. Inventory
try:
    r = requests.get(f"{API_URL}/api/inventory/items?page=1&per_page=5", timeout=3)
    tests.append(("✅ Inventory", r.status_code == 200 and len(r.json()) > 0))
except: tests.append(("❌ Inventory", False))

# 5. Orders
try:
    r = requests.get(f"{API_URL}/api/orders?page=1&per_page=5", timeout=3)
    tests.append(("✅ Orders", r.status_code == 200))
except: tests.append(("❌ Orders", False))

# 6. Analytics
try:
    r = requests.get(f"{API_URL}/api/analytics/dashboard", timeout=3)
    data = r.json()
    tests.append(("✅ Analytics", 'total_items' in data))
except: tests.append(("❌ Analytics", False))

# 7. Campaign Prediction (ML)
try:
    r = requests.post(f"{API_URL}/api/ml/campaigns/predict", json={
        "duration_days": 30,
        "points": 50,
        "discount_percent": 10,
        "minimum_spend": 100
    }, timeout=5)
    tests.append(("✅ Campaign ML", r.status_code == 200))
    if r.status_code == 200:
        data = r.json()
        redeem = data.get('data', {}).get('predictions', {}).get('expected_redemptions', 'N/A')
        print(f"   Redemptions: {redeem}", flush=True)
except: tests.append(("❌ Campaign ML", False))

print("\n" + "="*80, flush=True)
print("RESULTS", flush=True)
print("="*80, flush=True)
passed = sum(1 for _, result in tests if result)
for name, result in tests:
    print(f"{name}", flush=True)

print(f"\n📊 TOTAL: {passed}/{len(tests)} tests passed ({passed/len(tests)*100:.0f}%)", flush=True)
print("="*80, flush=True)
sys.stdout.flush()
