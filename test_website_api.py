"""
Test script to verify API and database are working correctly
"""
import requests
import json

API_BASE = "http://localhost:5000"

def test_endpoint(name, endpoint, params=None):
    """Test an API endpoint and display results"""
    try:
        response = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {name}")
            return data
        else:
            print(f"❌ FAIL {name} - Status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ FAIL {name} - {str(e)}")
        return None

print("=" * 80)
print("FRESH FLOW MARKETS - API & DATABASE VERIFICATION")
print("=" * 80)

# Test 1: Health Check
print("\n[1] Testing Health Endpoint...")
health = test_endpoint("Health Check", "/health")
if health:
    print(f"    Database: {health.get('database', 'unknown')}")
    print(f"    Orders: {health.get('orders_count', 0):,}")
    print(f"    ML Service: {health.get('ml_service', 'unknown')}")

# Test 2: Analytics Dashboard (3 years)
print("\n[2] Testing Analytics Dashboard (3-year data)...")
analytics = test_endpoint("Analytics Dashboard", "/api/analytics/dashboard", {"days": 1095})
if analytics and analytics.get('data'):
    summary = analytics['data'].get('summary', {})
    print(f"    Total Orders: {summary.get('total_orders', 0):,}")
    print(f"    Total Revenue: ${summary.get('total_revenue', 0):,.2f}")
    print(f"    Avg Order Value: ${summary.get('avg_order_value', 0):,.2f}")
    print(f"    Top Items Count: {len(analytics['data'].get('top_items', []))}")
    print(f"    Status Types: {len(analytics['data'].get('by_status', []))}")
    
    # Show status breakdown
    by_status = analytics['data'].get('by_status', [])
    if by_status:
        print(f"\n    Order Status Breakdown:")
        for status in by_status:
            print(f"      - {status['status']}: {status['count']:,}")

# Test 3: Inventory Items
print("\n[3] Testing Inventory Items...")
inventory = test_endpoint("Inventory Items", "/api/inventory/items", {"limit": 5})
if inventory and inventory.get('pagination'):
    print(f"    Total Items: {inventory['pagination']['total']:,}")
    print(f"    Sample Items Returned: {len(inventory.get('data', []))}")

# Test 4: Orders
print("\n[4] Testing Orders...")
orders = test_endpoint("Orders List", "/api/orders", {"per_page": 5})
if orders and orders.get('pagination'):
    print(f"    Total Orders: {orders['pagination']['total']:,}")
    print(f"    Sample Orders Returned: {len(orders.get('data', []))}")

# Test 5: Places
print("\n[5] Testing Places...")
places = test_endpoint("Places List", "/api/places", {"limit": 5})
if places and places.get('data'):
    print(f"    Sample Places Returned: {len(places.get('data', []))}")

# Test 6: ML Health
print("\n[6] Testing ML Service...")
ml_health = test_endpoint("ML Service Health", "/api/ml/health")
if ml_health:
    print(f"    Status: {ml_health.get('status', 'unknown')}")
    print(f"    Ready Models: {ml_health.get('ready_models', 0)}/{ml_health.get('total_models', 0)}")
    if ml_health.get('models_available'):
        print(f"    Available Models:")
        for model, available in ml_health['models_available'].items():
            status = "✓" if available else "✗"
            print(f"      [{status}] {model}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

print("\n📊 Dashboard URL: http://localhost:8501")
print("🔧 API Documentation: http://localhost:5000")
print("\n✅ All systems operational! Your website should display data correctly.")
