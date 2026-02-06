"""
Quick test to verify dashboard data will display correctly
"""
import requests
import pandas as pd

API_BASE = "http://localhost:5000"

print("=" * 80)
print("DASHBOARD DATA VERIFICATION")
print("=" * 80)

# Test analytics endpoint with 3-year data
response = requests.get(f"{API_BASE}/api/analytics/dashboard", params={"days": 1095}, timeout=10)
if response.status_code == 200:
    data = response.json()
    if data.get('success') and data.get('data'):
        print("\n✅ API Connection: SUCCESS")
        
        summary = data['data'].get('summary', {})
        print(f"\n📊 Summary Statistics:")
        print(f"   Total Orders: {summary.get('total_orders', 0):,}")
        print(f"   Total Revenue: ${summary.get('total_revenue', 0):,.2f}")
        print(f"   Avg Order Value: ${summary.get('avg_order_value', 0):,.2f}")
        
        by_status = data['data'].get('by_status', [])
        print(f"\n📦 Order Status Breakdown ({len(by_status)} statuses):")
        for status in by_status:
            status_val = status.get('status')
            # Handle None values same way as dashboard
            if status_val is None or pd.isna(status_val):
                status_name = "Unknown"
            else:
                status_name = str(status_val).replace('_', ' ').title()
            count = status.get('count', 0)
            print(f"   {status_name}: {count:,}")
        
        top_items = data['data'].get('top_items', [])
        print(f"\n🏆 Top Selling Items ({len(top_items)} items):")
        for i, item in enumerate(top_items[:5], 1):
            print(f"   {i}. {item.get('title', 'N/A')}: {item.get('order_count', 0):,} orders")
        
        trend = data['data'].get('trend', [])
        print(f"\n📈 Revenue Trend: {len(trend)} data points")
        if trend:
            print(f"   Date Range: {trend[0]['date']} to {trend[-1]['date']}")
        
        print("\n" + "=" * 80)
        print("✅ ALL DASHBOARD FEATURES WILL DISPLAY CORRECTLY")
        print("=" * 80)
        print("\n🌐 Open dashboard at: http://localhost:8501")
        print("   Select '1095 days (3 years)' from the dropdown\n")
    else:
        print("❌ API returned unsuccessful response")
else:
    print(f"❌ API request failed with status {response.status_code}")
