"""
Fresh Flow Markets API Server
Entry point for the REST API
"""

from src.api import create_app
from src.api.database import close_db

app = create_app()

# Register teardown function
app.teardown_appcontext(close_db)

if __name__ == '__main__':
    print("=" * 80)
    print("FRESH FLOW MARKETS API SERVER")
    print("=" * 80)
    print("\nStarting server...")
    print("API Documentation: http://localhost:5000/")
    print("Health Check: http://localhost:5000/health")
    print("\nEndpoints:")
    print("  - GET  /api/inventory/items         - List inventory items")
    print("  - GET  /api/inventory/items/<id>    - Get item details")
    print("  - PUT  /api/inventory/items/<id>    - Update item")
    print("  - GET  /api/inventory/low-stock     - Get low stock items")
    print("  - GET  /api/orders                  - List orders")
    print("  - GET  /api/orders/<id>             - Get order details")
    print("  - GET  /api/analytics/dashboard     - Dashboard stats")
    print("  - GET  /api/analytics/places        - Place analytics")
    print("  - POST /api/forecast/demand         - Demand forecast")
    print("  - GET  /api/places                  - List places")
    print("  - GET  /api/places/<id>             - Get place details")
    print("\n" + "=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
