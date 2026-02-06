import requests
import json

# Test inventory endpoint
print("Testing Inventory API...")
r = requests.get('http://localhost:5000/api/inventory/items?per_page=5')
print(f"Status: {r.status_code}")

data = r.json()
print(f"Success: {data.get('success')}")

if data.get('success'):
    items = data['data']
    print(f"Items returned: {len(items)}")
    print(f"Total items: {data['pagination']['total']}")
    
    if items:
        print(f"\nFirst item:")
        print(f"  Title: {items[0].get('title')}")
        print(f"  Price: ${items[0].get('price', 0):.2f}")
        print(f"  Status: {items[0].get('status')}")
else:
    print(f"Error: {data.get('error')}")

# Test search
print("\n" + "="*80)
print("Testing search...")
r = requests.get('http://localhost:5000/api/inventory/items?per_page=5&search=Sodavand')
data = r.json()
if data.get('success'):
    print(f"Search results: {len(data['data'])} items")
    if data['data']:
        print(f"First result: {data['data'][0].get('title')}")
else:
    print(f"Error: {data.get('error')}")
