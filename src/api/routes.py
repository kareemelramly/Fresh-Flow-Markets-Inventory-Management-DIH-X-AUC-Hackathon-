"""
Fresh Flow Markets - API Routes
Main REST API endpoints for inventory management
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from .database import query_db, query_df, execute_db
import pandas as pd

api_bp = Blueprint('api', __name__)

# ============================================================================
# INVENTORY ENDPOINTS
# ============================================================================

@api_bp.route('/inventory/items', methods=['GET'])
def get_inventory_items():
    """Get all inventory items with filtering and pagination"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        place_id = request.args.get('place_id', type=int)
        
        # Build query
        where_clauses = []
        params = []
        
        if search:
            where_clauses.append("(title LIKE ? OR number LIKE ?)")
            params.extend([f'%{search}%', f'%{search}%'])
        
        if place_id:
            where_clauses.append("place_id = ?")
            params.append(place_id)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM dim_items WHERE {where_sql}"
        total = query_db(count_query, params, one=True)['total']
        
        # Get items with pagination
        offset = (page - 1) * per_page
        query = f"""
            SELECT 
                id, title, accounting_reference, number AS barcode,
                price, vat, status,
                display_for_customers, delivery,
                eat_in, takeaway, created, updated
            FROM dim_items
            WHERE {where_sql}
            ORDER BY title
            LIMIT {per_page} OFFSET {offset}
        """
        
        items = query_db(query, params)
        
        return jsonify({
            'success': True,
            'data': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/inventory/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get single item details"""
    try:
        query = """
            SELECT 
                i.*,
                COUNT(DISTINCT oi.order_id) as times_ordered,
                SUM(oi.quantity) as total_quantity_sold
            FROM dim_items i
            LEFT JOIN fct_order_items oi ON i.id = oi.item_id
            WHERE i.id = ?
            GROUP BY i.id
        """
        item = query_db(query, [item_id], one=True)
        
        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404
        
        return jsonify({'success': True, 'data': item})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/inventory/low-stock', methods=['GET'])
def get_low_stock_items():
    """Get items with low stock levels based on order volume"""
    try:
        # Get items with low recent order activity (potential low stock indicators)
        query = """
            SELECT 
                i.id, 
                i.title, 
                i.number as barcode,
                i.price,
                i.status,
                COUNT(DISTINCT oi.order_id) as recent_orders,
                SUM(oi.quantity) as total_quantity_sold
            FROM dim_items i
            LEFT JOIN fct_order_items oi ON i.id = oi.item_id
            WHERE i.status = 'Active'
            GROUP BY i.id, i.title, i.number, i.price, i.status
            HAVING recent_orders < 10 OR recent_orders IS NULL
            ORDER BY recent_orders ASC, total_quantity_sold ASC
            LIMIT 100
        """
        items = query_db(query)
        
        return jsonify({
            'success': True,
            'data': items,
            'count': len(items)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/inventory/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Update item details"""
    try:
        data = request.json
        
        # Build update query dynamically
        allowed_fields = ['title', 'price', 'current_stock', 'minimum_stock', 
                         'description', 'barcode', 'stock_unit']
        
        updates = []
        params = []
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = ?")
                params.append(data[field])
        
        if not updates:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        
        # Add timestamp
        updates.append("updated = ?")
        params.append(int(datetime.now().timestamp()))
        
        # Add item_id for WHERE clause
        params.append(item_id)
        
        query = f"UPDATE dim_items SET {', '.join(updates)} WHERE id = ?"
        execute_db(query, params)
        
        # Return updated item
        updated_item = query_db("SELECT * FROM dim_items WHERE id = ?", [item_id], one=True)
        
        return jsonify({
            'success': True,
            'message': 'Item updated successfully',
            'data': updated_item
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ORDERS ENDPOINTS
# ============================================================================

@api_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get orders with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status = request.args.get('status')
        place_id = request.args.get('place_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = """
            SELECT 
                o.id, o.created, o.status, o.type, o.channel,
                o.total_amount, o.items_amount, o.discount_amount,
                o.delivery_charge, o.vat_amount, o.payment_method,
                o.user_id, o.place_id,
                p.title as place_name
            FROM fct_orders o
            LEFT JOIN dim_places p ON o.place_id = p.id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND o.status = ?"
            params.append(status)
        
        if place_id:
            query += " AND o.place_id = ?"
            params.append(place_id)
        
        if start_date:
            query += " AND o.created >= ?"
            params.append(int(datetime.fromisoformat(start_date).timestamp()))
        
        if end_date:
            query += " AND o.created <= ?"
            params.append(int(datetime.fromisoformat(end_date).timestamp()))
        
        # Count total
        count_query = f"SELECT COUNT(*) as total FROM ({query})"
        total = query_db(count_query, params, one=True)['total']
        
        # Add pagination
        offset = (page - 1) * per_page
        query += f" ORDER BY o.created DESC LIMIT {per_page} OFFSET {offset}"
        
        orders = query_db(query, params)
        
        return jsonify({
            'success': True,
            'data': orders,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details with items"""
    try:
        # Get order
        order_query = """
            SELECT 
                o.*,
                p.title as place_name,
                u.email as user_email,
                u.full_name as user_name
            FROM fct_orders o
            LEFT JOIN dim_places p ON o.place_id = p.id
            LEFT JOIN dim_users u ON o.user_id = u.id
            WHERE o.id = ?
        """
        order = query_db(order_query, [order_id], one=True)
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Get order items
        items_query = """
            SELECT 
                oi.*,
                i.title as item_name,
                i.barcode
            FROM fct_order_items oi
            LEFT JOIN dim_items i ON oi.item_id = i.id
            WHERE oi.order_id = ?
        """
        items = query_db(items_query, [order_id])
        
        order['items'] = items
        
        return jsonify({'success': True, 'data': order})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@api_bp.route('/analytics/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Date range (last 30 days by default)
        days = request.args.get('days', 30, type=int)
        start_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # Total orders
        orders_query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value,
                COUNT(DISTINCT user_id) as unique_customers
            FROM fct_orders
            WHERE created >= ?
        """
        stats = query_db(orders_query, [start_timestamp], one=True)
        
        # Orders by status
        status_query = """
            SELECT status, COUNT(*) as count
            FROM fct_orders
            WHERE created >= ?
            GROUP BY status
        """
        by_status = query_db(status_query, [start_timestamp])
        
        # Top selling items
        top_items_query = """
            SELECT 
                i.title,
                COUNT(DISTINCT oi.order_id) as order_count,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.price * oi.quantity) as revenue
            FROM fct_order_items oi
            JOIN dim_items i ON oi.item_id = i.id
            WHERE oi.created >= ?
            GROUP BY i.title
            ORDER BY order_count DESC
            LIMIT 10
        """
        top_items = query_db(top_items_query, [start_timestamp])
        
        # Revenue trend (daily)
        trend_query = """
            SELECT 
                DATE(created, 'unixepoch') as date,
                COUNT(*) as orders,
                SUM(total_amount) as revenue
            FROM fct_orders
            WHERE created >= ?
            GROUP BY date
            ORDER BY date
        """
        trend = query_db(trend_query, [start_timestamp])
        
        return jsonify({
            'success': True,
            'data': {
                'summary': stats,
                'by_status': by_status,
                'top_items': top_items,
                'trend': trend,
                'period_days': days
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics/places', methods=['GET'])
def get_places_analytics():
    """Get analytics by place/restaurant"""
    try:
        days = request.args.get('days', 30, type=int)
        start_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        query = """
            SELECT 
                p.id,
                p.title as place_name,
                COUNT(DISTINCT o.id) as total_orders,
                COUNT(DISTINCT o.user_id) as unique_customers,
                SUM(o.total_amount) as total_revenue,
                AVG(o.total_amount) as avg_order_value,
                SUM(o.items_amount) as items_revenue,
                SUM(o.delivery_charge) as delivery_revenue
            FROM dim_places p
            LEFT JOIN fct_orders o ON p.id = o.place_id AND o.created >= ?
            GROUP BY p.id, p.title
            HAVING total_orders > 0
            ORDER BY total_revenue DESC
        """
        places = query_db(query, [start_timestamp])
        
        return jsonify({
            'success': True,
            'data': places,
            'period_days': days
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# FORECAST ENDPOINT
# ============================================================================

@api_bp.route('/forecast/demand', methods=['POST'])
def forecast_demand():
    """Forecast demand for items (simple moving average)"""
    try:
        data = request.json
        item_id = data.get('item_id')
        days_ahead = data.get('days', 7)
        
        if not item_id:
            return jsonify({'success': False, 'error': 'item_id required'}), 400
        
        # Get historical data (last 30 days)
        query = """
            SELECT 
                DATE(oi.created, 'unixepoch') as date,
                SUM(oi.quantity) as quantity
            FROM fct_order_items oi
            WHERE oi.item_id = ?
                AND oi.created >= ?
            GROUP BY date
            ORDER BY date
        """
        
        start_ts = int((datetime.now() - timedelta(days=30)).timestamp())
        historical = query_df(query, [item_id, start_ts])
        
        if len(historical) == 0:
            return jsonify({
                'success': False,
                'error': 'No historical data available for this item'
            }), 404
        
        # Simple moving average forecast
        avg_daily_demand = historical['quantity'].mean()
        
        # Generate forecast
        forecast = []
        for i in range(1, days_ahead + 1):
            forecast_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            forecast.append({
                'date': forecast_date,
                'predicted_quantity': round(avg_daily_demand, 2)
            })
        
        # Get item details
        item = query_db("SELECT id, title, current_stock, minimum_stock FROM dim_items WHERE id = ?", 
                       [item_id], one=True)
        
        return jsonify({
            'success': True,
            'data': {
                'item': item,
                'historical_avg_daily': round(avg_daily_demand, 2),
                'forecast': forecast,
                'recommendation': {
                    'reorder_needed': item.get('current_stock', 0) < (avg_daily_demand * days_ahead),
                    'suggested_reorder_qty': round(avg_daily_demand * days_ahead * 1.2, 0)
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# PLACES ENDPOINTS
# ============================================================================

@api_bp.route('/places', methods=['GET'])
def get_places():
    """Get all places/restaurants"""
    try:
        query = """
            SELECT 
                id, title, active, country, currency,
                street_address, phone, email, website,
                delivery, takeaway, eat_in
            FROM dim_places
            WHERE active = 1
            ORDER BY title
        """
        places = query_db(query)
        
        return jsonify({
            'success': True,
            'data': places,
            'count': len(places)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/places/<int:place_id>', methods=['GET'])
def get_place(place_id):
    """Get place details"""
    try:
        place = query_db("SELECT * FROM dim_places WHERE id = ?", [place_id], one=True)
        
        if not place:
            return jsonify({'success': False, 'error': 'Place not found'}), 404
        
        # Get place statistics
        stats_query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount) as total_revenue,
                COUNT(DISTINCT user_id) as unique_customers
            FROM fct_orders
            WHERE place_id = ?
        """
        stats = query_db(stats_query, [place_id], one=True)
        
        place['statistics'] = stats
        
        return jsonify({'success': True, 'data': place})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
