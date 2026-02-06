"""Final System Status Report"""
import requests

URL = "http://localhost:5000"

print("="*80)
print("FRESH FLOW MARKETS - SYSTEM STATUS REPORT")
print("="*80)

# Test 7 key endpoints
results = []

# 1. API Health
try:
    r = requests.get(f"{URL}/health", timeout=10)
    results.append(("API Health", "✅" if r.status_code == 200 else "❌"))
except:
    results.append(("API Health", "❌"))

# 2. Database
try:
    r = requests.get(f"{URL}/api/analytics/dashboard", timeout=10)
    data = r.json()
    results.append((f"Database ({data.get('total_orders', 0):,} orders)", "✅"))
except:
    results.append(("Database", "❌"))

# 3. Inventory API
try:
    r = requests.get(f"{URL}/api/inventory/items?page=1&per_page=1", timeout=10)
    results.append(("Inventory API", "✅" if r.status_code == 200 else "❌"))
except:
    results.append(("Inventory API", "❌"))

# 4. Orders API
try:
    r = requests.get(f"{URL}/api/orders?page=1&per_page=1", timeout=10)
    results.append(("Orders API", "✅" if r.status_code == 200 else "❌"))
except:
    results.append(("Orders API", "❌"))

# 5. ML Service
try:
    r = requests.get(f"{URL}/api/ml/health", timeout=10)
    data = r.json()
    ready = data.get('ready_models', 0)
    results.append((f"ML Service ({ready}/4 models)", "✅" if r.status_code == 200 else "❌"))
except:
    results.append(("ML Service", "❌"))

# 6. Campaign ROI Model  
try:
    r = requests.post(f"{URL}/api/ml/campaigns/predict", json={
        "duration_days": 30,
        "points": 50,
        "discount_percent": 10,
        "minimum_spend": 100
    }, timeout=15)
    data = r.json()
    redeem = data.get('data', {}).get('predictions', {}).get('expected_redemptions', 0)
    results.append((f"Campaign ROI Model (predicts {redeem})", "✅"))
except:
    results.append(("Campaign ROI Model", "❌"))

# 7. CORS (for web)
try:
    r = requests.options(f"{URL}/api/ml/campaigns/predict", timeout=10)
    cors = r.headers.get('Access-Control-Allow-Origin',  '')
    results.append(("CORS (Web Integration)", "✅" if cors == '*' else "❌"))
except:
    results.append(("CORS", "❌"))

# Print Results
print("\n STATUS CHECK")
print("-"*80)
for name, status in results:
    print(f"  {status}  {name}")

passed = sum(1 for _, s in results if s == "✅")
print("-"*80)
print(f"\n  📊 OVERALL: {passed}/{len(results)} Systems Ready ({passed/len(results)*100:.0f}%)\n")
print("="*80)
