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
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # Register blueprints
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return {
            'service': 'Fresh Flow Markets API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'inventory': '/api/inventory',
                'orders': '/api/orders',
                'analytics': '/api/analytics',
                'forecast': '/api/forecast',
                'places': '/api/places'
            }
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
            return {'status': 'healthy', 'database': 'connected', 'orders_count': count}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500
    
    return app
