"""
Fresh Flow Markets - ML Prediction API Routes
REST API endpoints for all machine learning models
"""

from flask import Blueprint, request, jsonify
from ..services.ml_prediction_service import MLPredictionService
from .database import query_db
from datetime import datetime
import traceback

ml_bp = Blueprint('ml', __name__)

# Initialize ML service
ml_service = MLPredictionService(models_dir='ML_Models')

# ============================================================================
# HEALTH CHECK & STATUS
# ============================================================================

@ml_bp.route('/health', methods=['GET'])
def ml_health_check():
    """Check ML service health and available models"""
    try:
        health = ml_service.health_check()
        return jsonify(health), 200
    except Exception as e:
        return jsonify({
            'service': 'ML Prediction Service',
            'status': 'error',
            'error': str(e)
        }), 500

@ml_bp.route('/models/status', methods=['GET'])
def get_models_status():
    """Get detailed status of all ML models"""
    try:
        models_status = ml_service.get_available_models()
        
        return jsonify({
            'success': True,
            'models': {
                'demand_forecast': {
                    'available': models_status['demand_forecast'],
                    'name': 'Dynamic Demand & Stock Forecaster',
                    'type': 'Regression/Time-Series',
                    'description': 'Predicts item demand to prevent low stock situations'
                },
                'campaign_roi': {
                    'available': models_status['campaign_roi'],
                    'name': 'Campaign ROI & Redemption Predictor',
                    'type': 'Classification/Regression',
                    'description': 'Predicts campaign success probability and redemption frequency'
                },
                'customer_churn': {
                    'available': models_status['customer_churn'],
                    'name': 'Customer Churn & Loyalty Scorer',
                    'type': 'Classification',
                    'description': 'Identifies customers likely to stop ordering'
                },
                'cashier_risk': {
                    'available': models_status['cashier_risk'],
                    'name': 'Operational Risk & Cashier Integrity Monitor',
                    'type': 'Anomaly Detection',
                    'description': 'Flags unusual transactions suggesting operational risks'
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# 1. DEMAND & STOCK FORECASTING ENDPOINTS
# ============================================================================

@ml_bp.route('/forecast/demand', methods=['POST'])
def predict_item_demand():
    """
    Predict demand for a specific item
    
    Request Body:
    {
        "item_id": 123,
        "forecast_days": 7,
        "is_holiday": false,
        "is_weekend": false,
        "campaign_active": false,
        "price": 99.99
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        if 'item_id' not in data:
            return jsonify({'success': False, 'error': 'item_id is required'}), 400
        
        # Get item details from database
        item = query_db(
            "SELECT id, title, price FROM dim_items WHERE id = ?",
            [data['item_id']],
            one=True
        )
        
        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404
        
        # Use item price if not provided
        price = data.get('price', item.get('price'))
        
        # Predict demand (pass item name for category mapping)
        forecast = ml_service.predict_demand(
            item_id=data['item_id'],
            forecast_days=data.get('forecast_days', 7),
            is_holiday=data.get('is_holiday', False),
            is_weekend=data.get('is_weekend', False),
            campaign_active=data.get('campaign_active', False),
            price=price,
            item_name=item.get('title')  # Add item name for model matching
        )
        
        # Check if prediction failed
        if forecast.get('status') == 'error':
            return jsonify({
                'success': False,
                'error': forecast.get('error', 'Prediction failed'),
                'details': {
                    'item_id': forecast.get('item_id'),
                    'category_attempted': forecast.get('category_attempted')
                }
            }), 400
        
        # Add item details to response
        forecast['item_details'] = {
            'id': item['id'],
            'name': item['title'],
            'current_price': item.get('price')
        }
        
        return jsonify({'success': True, 'data': forecast})
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@ml_bp.route('/forecast/reorder-recommendations', methods=['POST'])
def get_reorder_recommendations():
    """
    Get stock reorder recommendations
    
    Request Body:
    {
        "item_id": 123,
        "current_stock": 50.5,
        "lead_time_days": 3,
        "safety_stock_multiplier": 1.2
    }
    """
    try:
        data = request.json
        
        if 'item_id' not in data:
            return jsonify({'success': False, 'error': 'item_id is required'}), 400
        
        # Require current_stock to be provided
        if 'current_stock' not in data:
            return jsonify({
                'success': False,
                'error': 'current_stock is required'
            }), 400
        
        current_stock = data['current_stock']
        
        # Get item details from database for item_name
        item = query_db(
            "SELECT id, title FROM dim_items WHERE id = ?",
            [data['item_id']],
            one=True
        )
        
        # Get recommendations (pass item_name for category-based forecasting)
        recommendations = ml_service.get_reorder_recommendations(
            item_id=data['item_id'],
            current_stock=current_stock,
            lead_time_days=data.get('lead_time_days', 3),
            safety_stock_multiplier=data.get('safety_stock_multiplier', 1.2),
            item_name=item.get('title') if item else None
        )
        
        # Check if recommendation failed
        if recommendations.get('status') == 'error':
            return jsonify({
                'success': False,
                'error': recommendations.get('error', 'Cannot generate reorder recommendations'),
                'details': {
                    'item_id': recommendations.get('item_id')
                }
            }), 400
        
        return jsonify({'success': True, 'data': recommendations})
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@ml_bp.route('/forecast/bulk-items', methods=['POST'])
def bulk_forecast_demand():
    """
    Get demand forecasts for multiple items at once
    
    Request Body:
    {
        "item_ids": [123, 456, 789],
        "forecast_days": 7
    }
    """
    try:
        data = request.json
        
        if 'item_ids' not in data or not isinstance(data['item_ids'], list):
            return jsonify({'success': False, 'error': 'item_ids array is required'}), 400
        
        forecasts = []
        for item_id in data['item_ids']:
            try:
                # Get item details for category mapping
                item = query_db(
                    "SELECT id, title FROM dim_items WHERE id = ?",
                    [item_id],
                    one=True
                )
                
                item_name = item.get('title') if item else None
                
                forecast = ml_service.predict_demand(
                    item_id=item_id,
                    forecast_days=data.get('forecast_days', 7),
                    item_name=item_name
                )
                forecasts.append(forecast)
            except Exception as e:
                forecasts.append({
                    'status': 'error',
                    'item_id': item_id,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'total_items': len(data['item_ids']),
            'forecasts': forecasts
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# 2. CAMPAIGN ROI & REDEMPTION PREDICTION ENDPOINTS
# ============================================================================

@ml_bp.route('/campaigns/predict', methods=['POST'])
def predict_campaign():
    """
    Predict campaign performance
    
    Request Body:
    {
        "duration_days": 7,
        "points": 200,
        "discount_percent": 20,
        "minimum_spend": 100
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['duration_days', 'points', 'discount_percent', 'minimum_spend']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Predict
        prediction = ml_service.predict_campaign_performance(
            duration_days=data['duration_days'],
            points=data['points'],
            discount_percent=data['discount_percent'],
            minimum_spend=data['minimum_spend']
        )
        
        return jsonify({'success': True, 'data': prediction})
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@ml_bp.route('/campaigns/optimize', methods=['POST'])
def optimize_campaign():
    """
    Find optimal campaign parameters
    
    Request Body:
    {
        "target_redemptions": 25,
        "max_discount": 30,
        "budget_per_redemption": 100
    }
    """
    try:
        data = request.json
        
        optimization = ml_service.optimize_campaign_parameters(
            target_redemptions=data.get('target_redemptions', 25),
            max_discount=data.get('max_discount', 30),
            budget_per_redemption=data.get('budget_per_redemption', 100)
        )
        
        return jsonify({'success': True, 'data': optimization})
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@ml_bp.route('/campaigns/batch-predict', methods=['POST'])
def batch_predict_campaigns():
    """
    Predict performance for multiple campaign scenarios
    
    Request Body:
    {
        "campaigns": [
            {"duration_days": 3, "points": 100, "discount_percent": 10, "minimum_spend": 50},
            {"duration_days": 7, "points": 200, "discount_percent": 20, "minimum_spend": 100}
        ]
    }
    """
    try:
        data = request.json
        
        if 'campaigns' not in data or not isinstance(data['campaigns'], list):
            return jsonify({'success': False, 'error': 'campaigns array is required'}), 400
        
        predictions = []
        for idx, campaign in enumerate(data['campaigns']):
            try:
                prediction = ml_service.predict_campaign_performance(
                    duration_days=campaign['duration_days'],
                    points=campaign['points'],
                    discount_percent=campaign['discount_percent'],
                    minimum_spend=campaign['minimum_spend']
                )
                prediction['campaign_index'] = idx
                predictions.append(prediction)
            except Exception as e:
                predictions.append({
                    'status': 'error',
                    'campaign_index': idx,
                    'error': str(e)
                })
        
        # Sort by success probability
        successful_predictions = [p for p in predictions if p.get('status') == 'success']
        successful_predictions.sort(
            key=lambda x: x['predictions']['success_probability'],
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'total_campaigns': len(data['campaigns']),
            'predictions': predictions,
            'best_campaign': successful_predictions[0] if successful_predictions else None
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# 3. CUSTOMER CHURN & LOYALTY PREDICTION ENDPOINTS
# ============================================================================

@ml_bp.route('/customers/churn-risk', methods=['POST'])
def predict_churn_risk():
    """
    Predict customer churn risk
    
    Request Body:
    {
        "customer_id": 123,
        "discount_amount": 1000.50,
        "points_earned": 5000.0,
        "points_redeemed": 2500.0,
        "price": 150.75,
        "waiting_time": 25.5,
        "vip_threshold": 3000.0,
        "rating": 4.2
    }
    """
    try:
        data = request.json
        
        # Validate required fields (model uses 4 features)
        required_fields = [
            'customer_id', 'discount_amount', 'points_earned',
            'price', 'waiting_time'
        ]
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Predict churn
        prediction = ml_service.predict_customer_churn(
            customer_id=data['customer_id'],
            discount_amount=data['discount_amount'],
            points_earned=data['points_earned'],
            price=data['price'],
            waiting_time=data['waiting_time']
        )
        
        return jsonify({'success': True, 'data': prediction})
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@ml_bp.route('/customers/batch-churn-risk', methods=['POST'])
def batch_predict_churn():
    """
    Predict churn risk for multiple customers
    
    Request Body:
    {
        "customers": [
            {
                "customer_id": 123,
                "recent_waiting_time": 25.5,
                "recent_rating": 3.5,
                "points_redeemed": 500,
                "vip_threshold": 1000,
                "days_since_last_order": 15
            }
        ]
    }
    """
    try:
        data = request.json
        
        if 'customers' not in data or not isinstance(data['customers'], list):
            return jsonify({'success': False, 'error': 'customers array is required'}), 400
        
        predictions = []
        for customer in data['customers']:
            try:
                prediction = ml_service.predict_customer_churn(**customer)
                predictions.append(prediction)
            except Exception as e:
                predictions.append({
                    'status': 'error',
                    'customer_id': customer.get('customer_id'),
                    'error': str(e)
                })
        
        # Sort by churn risk (highest first)
        high_risk_customers = [
            p for p in predictions
            if p.get('status') == 'success' and p['churn_risk']['probability'] >= 50
        ]
        high_risk_customers.sort(
            key=lambda x: x['churn_risk']['probability'],
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'total_customers': len(data['customers']),
            'predictions': predictions,
            'high_risk_count': len(high_risk_customers),
            'high_risk_customers': high_risk_customers
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# 4. OPERATIONAL RISK & CASHIER INTEGRITY ENDPOINTS
# ============================================================================

@ml_bp.route('/operations/cashier-risk', methods=['POST'])
def detect_cashier_risk():
    """
    Detect cashier anomalies and operational risks
    
    Request Body:
    {
        "cashier_id": 45,
        "shift_date": "2026-02-05",
        "balance_diff_sum": 101066.0,
        "balance_diff_mean": 66.0,
        "balance_diff_std": 50.0,
        "balance_diff_min": -100.0,
        "balance_diff_max": 200.0,
        "balance_discrepancy_pct_mean": 10.5,
        "balance_discrepancy_pct_max": 27100.0,
        "transaction_total_sum": 213647.75,
        "transaction_total_count": 1531,
        "transaction_total_mean": 139.5,
        "vat_component_sum": 32047.16,
        "num_transactions_sum": 1531,
        "opening_balance_mean": 1000.0,
        "closing_balance_mean": 50000.0,
        "id_count": 1,
        "total_amount_sum": 213647.75,
        "total_amount_mean": 139.5,
        "total_amount_std": 45.2,
        "cash_amount_sum": 150000.0,
        "cash_amount_mean": 98.0
    }
    """
    try:
        data = request.json
        
        # Validate required fields (all 20 features)
        required_fields = [
            'cashier_id', 'shift_date', 
            'balance_diff_sum', 'balance_diff_mean', 'balance_diff_std',
            'balance_diff_min', 'balance_diff_max',
            'balance_discrepancy_pct_mean', 'balance_discrepancy_pct_max',
            'transaction_total_sum', 'transaction_total_count', 'transaction_total_mean',
            'vat_component_sum', 'num_transactions_sum',
            'opening_balance_mean', 'closing_balance_mean', 'id_count',
            'total_amount_sum', 'total_amount_mean', 'total_amount_std',
            'cash_amount_sum', 'cash_amount_mean'
        ]
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Detect anomalies
        detection = ml_service.detect_cashier_anomalies(
            cashier_id=data['cashier_id'],
            shift_date=data['shift_date'],
            balance_diff_sum=data['balance_diff_sum'],
            balance_diff_mean=data['balance_diff_mean'],
            balance_diff_std=data['balance_diff_std'],
            balance_diff_min=data['balance_diff_min'],
            balance_diff_max=data['balance_diff_max'],
            balance_discrepancy_pct_mean=data['balance_discrepancy_pct_mean'],
            balance_discrepancy_pct_max=data['balance_discrepancy_pct_max'],
            transaction_total_sum=data['transaction_total_sum'],
            transaction_total_count=data['transaction_total_count'],
            transaction_total_mean=data['transaction_total_mean'],
            vat_component_sum=data['vat_component_sum'],
            num_transactions_sum=data['num_transactions_sum'],
            opening_balance_mean=data['opening_balance_mean'],
            closing_balance_mean=data['closing_balance_mean'],
            id_count=data['id_count'],
            total_amount_sum=data['total_amount_sum'],
            total_amount_mean=data['total_amount_mean'],
            total_amount_std=data['total_amount_std'],
            cash_amount_sum=data['cash_amount_sum'],
            cash_amount_mean=data['cash_amount_mean']
        )
        
        return jsonify({'success': True, 'data': detection})
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@ml_bp.route('/operations/cashier-risk-lookup/<int:cashier_id>', methods=['GET'])
def get_cashier_risk_lookup(cashier_id):
    """
    Quick lookup of pre-calculated cashier risk assessment
    
    URL Parameter:
        cashier_id: The cashier user ID to look up
    
    Response:
    {
        "success": true,
        "data": {
            "cashier_id": 22354,
            "risk_level": 1,
            "risk_probability": 1.0,
            "risk_category": "CRITICAL",
            "balance_discrepancy_pct_max": 27100.0,
            "balance_diff_sum": 101066.0,
            "num_transactions_sum": 1531.0,
            "transaction_total_sum": 213647.75,
            "vat_component_sum": 32047.1625,
            "anomaly_score": -0.3297787310026391
        }
    }
    """
    try:
        # Get pre-calculated risk assessment from CSV
        assessment = ml_service.get_cashier_risk_from_csv(cashier_id)
        
        if assessment:
            return jsonify({'success': True, 'data': assessment})
        else:
            return jsonify({
                'success': False,
                'error': f'Cashier {cashier_id} not found in pre-calculated assessments'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@ml_bp.route('/operations/batch-cashier-risk', methods=['POST'])
def batch_detect_cashier_risk():
    """
    Detect risks for multiple cashier shifts
    
    Request Body:
    {
        "shifts": [
            {
                "cashier_id": 45,
                "shift_date": "2026-02-05",
                "order_count": 150,
                "expected_balance": 15000.00,
                "actual_balance": 14850.00,
                "total_vat": 3000.00
            }
        ]
    }
    """
    try:
        data = request.json
        
        if 'shifts' not in data or not isinstance(data['shifts'], list):
            return jsonify({'success': False, 'error': 'shifts array is required'}), 400
        
        detections = []
        for shift in data['shifts']:
            try:
                detection = ml_service.detect_cashier_anomalies(**shift)
                detections.append(detection)
            except Exception as e:
                detections.append({
                    'status': 'error',
                    'cashier_id': shift.get('cashier_id'),
                    'shift_date': shift.get('shift_date'),
                    'error': str(e)
                })
        
        # Filter high-risk shifts
        critical_risks = [
            d for d in detections
            if d.get('status') == 'success' and d['risk_assessment']['risk_level'] in ['critical', 'high']
        ]
        critical_risks.sort(
            key=lambda x: x['risk_assessment']['risk_score'],
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'total_shifts': len(data['shifts']),
            'detections': detections,
            'critical_risk_count': len(critical_risks),
            'critical_risks': critical_risks
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@ml_bp.route('/predictions/history', methods=['GET'])
def get_prediction_history():
    """Get recent prediction history (placeholder for future implementation)"""
    return jsonify({
        'success': True,
        'message': 'Prediction history logging not yet implemented',
        'data': []
    })

@ml_bp.route('/models/retrain', methods=['POST'])
def trigger_model_retrain():
    """Trigger model retraining (placeholder for future implementation)"""
    return jsonify({
        'success': True,
        'message': 'Model retraining endpoint - to be implemented with scheduled jobs',
        'recommendation': 'Use dedicated training notebooks for model retraining'
    })
