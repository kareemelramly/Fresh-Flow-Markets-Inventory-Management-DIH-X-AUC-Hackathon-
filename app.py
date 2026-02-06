"""
Fresh Flow Markets API Server
Entry point for the REST API
"""

from src.api import create_app
from src.api.database import close_db

app = create_app(db_path='database/fresh_flow_markets.db')

# Register teardown function
app.teardown_appcontext(close_db)

if __name__ == '__main__':
    print("=" * 80)
    print("FRESH FLOW MARKETS API SERVER v2.0")
    print("=" * 80)
    print("\nStarting server...")
    print("API Documentation: http://localhost:5000/")
    print("Health Check: http://localhost:5000/health")
    print("ML Service Health: http://localhost:5000/api/ml/health")
    
    print("\n" + "=" * 80)
    print("STANDARD API ENDPOINTS")
    print("=" * 80)
    print("  - GET  /api/inventory/items         - List inventory items")
    print("  - GET  /api/inventory/items/<id>    - Get item details")
    print("  - PUT  /api/inventory/items/<id>    - Update item")
    print("  - GET  /api/inventory/low-stock     - Get low stock items")
    print("  - GET  /api/orders                  - List orders")
    print("  - GET  /api/orders/<id>             - Get order details")
    print("  - GET  /api/analytics/dashboard     - Dashboard stats")
    print("  - GET  /api/analytics/places        - Place analytics")
    print("  - GET  /api/places                  - List places")
    print("  - GET  /api/places/<id>             - Get place details")
    
    print("\n" + "=" * 80)
    print("MACHINE LEARNING PREDICTION ENDPOINTS")
    print("=" * 80)
    print("\n🔹 1. Demand & Stock Forecasting")
    print("  - POST /api/ml/forecast/demand                - Predict item demand")
    print("  - POST /api/ml/forecast/reorder-recommendations - Get reorder advice")
    print("  - POST /api/ml/forecast/bulk-items            - Bulk demand forecast")
    
    print("\n🔹 2. Campaign ROI & Redemption Prediction")
    print("  - POST /api/ml/campaigns/predict              - Predict campaign performance")
    print("  - POST /api/ml/campaigns/optimize             - Find optimal parameters")
    print("  - POST /api/ml/campaigns/batch-predict        - Batch campaign predictions")
    
    print("\n🔹 3. Customer Churn & Loyalty Scoring")
    print("  - POST /api/ml/customers/churn-risk           - Predict churn probability")
    print("  - POST /api/ml/customers/batch-churn-risk     - Batch churn predictions")
    
    print("\n🔹 4. Operational Risk & Cashier Integrity")
    print("  - POST /api/ml/operations/cashier-risk        - Detect cashier anomalies")
    print("  - POST /api/ml/operations/batch-cashier-risk  - Batch risk detection")
    
    print("\n🔹 ML Service Status")
    print("  - GET  /api/ml/health                         - ML service health")
    print("  - GET  /api/ml/models/status                  - Available models status")
    
    print("\n" + "=" * 80)
    print("Ready for website integration!")
    print("All endpoints support CORS for web applications")
    print("=" * 80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
