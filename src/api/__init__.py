"""
Fresh Flow Markets - REST API
Inventory Management System API
"""

from flask import Flask
from flask_cors import CORS
import sqlite3

def create_app(db_path='fresh_flow_markets.db'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config['DATABASE'] = db_path
    app.config['JSON_SORT_KEYS'] = False
    
    # Enable CORS for frontend integration with comprehensive settings
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": False,
            "max_age": 3600
        }
    })
    
    # Register blueprints
    from .routes import api_bp
    from .ml_routes import ml_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    
    @app.route('/')
    def index():
        return {
            'service': 'Fresh Flow Markets API',
            'version': '2.0.0',
            'status': 'running',
            'description': 'Inventory Management & ML Prediction API',
            'endpoints': {
                'inventory': '/api/inventory',
                'orders': '/api/orders',
                'analytics': '/api/analytics',
                'forecast': '/api/forecast',
                'places': '/api/places',
                'ml_predictions': '/api/ml',
                'ml_health': '/api/ml/health',
                'ml_models_status': '/api/ml/models/status'
            },
            'ml_models': {
                'demand_forecast': '/api/ml/forecast/demand',
                'campaign_prediction': '/api/ml/campaigns/predict',
                'customer_churn': '/api/ml/customers/churn-risk',
                'cashier_risk': '/api/ml/operations/cashier-risk'
            },
            'documentation': '/docs/API_DOCUMENTATION.md'
        }
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        try:
            conn = sqlite3.connect(app.config['DATABASE'])
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM fct_orders")
            count = cursor.fetchone()[0]
            conn.close()
            return {
                'status': 'healthy',
                'database': 'connected',
                'orders_count': count,
                'api_version': '2.0.0',
                'ml_service': 'available'
            }
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500
    
    return app
