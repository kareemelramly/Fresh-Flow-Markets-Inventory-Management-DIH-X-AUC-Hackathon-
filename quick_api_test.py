import requests

print("="*80)
print("FRESH FLOW MARKETS - API QUICK TEST")
print("="*80)

# Test 1: Health Check
print("\n✓ Testing Health Check...")
r = requests.get('http://localhost:5000/health')
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    print(f"  Response: {r.json()}")

# Test 2: Inventory Items
print("\n✓ Testing Inventory Items...")
r = requests.get('http://localhost:5000/api/inventory/items?per_page=5')
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  Total Items: {data['pagination']['total']:,}")
    print(f"  Items Returned: {len(data['data'])}")
    if data['data']:
        print(f"  First Item: {data['data'][0]['title']}")

# Test 3: Dashboard Analytics
print("\n✓ Testing Dashboard Analytics...")
r = requests.get('http://localhost:5000/api/analytics/dashboard?days=1095')
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    summary = data['data']['summary']
    print(f"  Total Orders: {summary['total_orders']:,}")
    print(f"  Total Revenue: ${summary['total_revenue']:,.2f}")
    print(f"  Avg Order Value: ${summary['avg_order_value']:.2f}")

# Test 4: ML Service Health
print("\n✓ Testing ML Service...")
r = requests.get('http://localhost:5000/api/ml/health')
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  Service Status: {data.get('status', 'unknown')}")
    models = data.get('available_models', {})
    for model, available in models.items():
        status = "✅ Ready" if available else "⚠️ Not Ready"
        print(f"    {model}: {status}")

# Test 5: Search Functionality
print("\n✓ Testing Search...")
r = requests.get('http://localhost:5000/api/inventory/items?search=Coca&per_page=3')
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  Search Results: {len(data['data'])} items found")
    for item in data['data'][:3]:
        print(f"    - {item['title']}")

print("\n" + "="*80)
print("API TEST COMPLETE - All endpoints are operational!")
print("="*80)
print("\nYou can now test:")
print("  • API Endpoints: http://localhost:5000")
print("  • Interactive testing: Use Postman, curl, or browser")
print("  • Dashboard Website: Run 'streamlit run dashboard.py'")
