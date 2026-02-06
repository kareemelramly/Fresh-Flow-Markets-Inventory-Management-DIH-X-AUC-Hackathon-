import requests
import sys

URL = "http://localhost:5000"
print("Testing API...", flush=True)

# Test 1: Health
print("1. Health... ", end='', flush=True)
try:
    r = requests.get(f"{URL}/health", timeout=5)
    print("✅", flush=True)
except Exception as e:
    print(f"❌ {e}", flush=True)

# Test 2: Campaign ML
print("2. Campaign ML... ", end='', flush=True)
try:
    r = requests.post(f"{URL}/api/ml/campaigns/predict", 
                     json={"duration_days": 30, "points": 50, "discount_percent": 10, "minimum_spend": 100},
                     timeout=10)
    if r.status_code == 200:
        data = r.json()
        redeem = data.get('data', {}).get('predictions', {}).get('expected_redemptions', 0)
        print(f"✅ Predicts {redeem} redemptions", flush=True)
    else:
        print(f"❌ Status {r.status_code}", flush=True)
except Exception as e:
    print(f"❌ {e}", flush=True)

# Test 3: Database
print("3. Database... ", end='', flush=True)
try:
    r = requests.get(f"{URL}/api/analytics/dashboard", timeout=5)
    data = r.json()
    print(f"✅ {data.get('total_orders', 0):,} orders", flush=True)
except Exception as e:
    print(f"❌ {e}", flush=True)

print("\nDONE", flush=True)
sys.stdout.flush()
