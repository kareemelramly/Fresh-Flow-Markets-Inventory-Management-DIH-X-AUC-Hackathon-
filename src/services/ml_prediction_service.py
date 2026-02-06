"""
Fresh Flow Markets - Machine Learning Prediction Service
Unified service for all ML model predictions
"""

import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

class MLPredictionService:
    """
    Unified ML prediction service supporting all Fresh Flow Markets models:
    1. Demand & Stock Forecaster
    2. Campaign ROI & Redemption Predictor
    3. Customer Churn & Loyalty Scorer
    4. Operational Risk & Cashier Integrity Monitor
    """
    
    def __init__(self, models_dir: str = 'ML_Models'):
        """Initialize the ML prediction service"""
        self.models_dir = models_dir
        self.loaded_models = {}
        self.model_configs = {
            'campaign_roi': {
                'base_path': 'Campaign_ROI_Predictor/models',
                'regressor': 'campaign_redemption_regressor.pkl',
                'classifier': 'campaign_success_classifier.pkl',
                'scaler': 'campaign_scaler.pkl',
                'features': 'campaign_features.pkl'
            },
            'demand_forecast': {
                'base_path': 'stock_forecaster/models',
                'model_type': 'xgb',  # XGBoost models
                'models_subdir': 'xgb_models',
                'scalers_subdir': 'scalers'
            },
            'customer_churn': {
                'base_path': 'customer_churn',
                'bundle': 'model_bundle.joblib'  # Single bundle file
            },
            'cashier_risk': {
                'base_path': 'Operational_risk_predictors/models',
                'model': 'random_forest_model(preferred).pkl',
                'scaler': 'feature_scaler.pkl',
                'features': 'feature_columns.pkl'
            }
        }
        # Cache for item-specific forecast models
        self.item_forecast_models = {}
        
        # Category mapping for items without specific models
        self.category_keywords = {
            'Sodavand': ['cola', 'sodavand', 'naturfrisk', 'lemonade', 'fanta', 'sprite', 'pepsi', 'soda'],
            'Vand': ['water', 'vand', 'kildevand', 'still water', 'sparkling'],
            'Øl': ['øl', 'beer', 'fadøl', 'pilsner', 'ipa', 'lager', 'ale'],
            'Cappuccino': ['cappuccino', 'latte', 'americano', 'kaffe', 'espresso', 'coffee', 'flat white'],
            'Lille_box': ['lille box', 'small box', 'lille'],
            'Mellem_box': ['mellem box', 'medium box', 'mellem', 'stor box', 'large box'],
            'Ristet_Hotdog': ['hotdog', 'ristet', 'fransk', 'pølse'],
            'Øl_Vand_Spiritus': ['spiritus', 'vodka', 'gin', 'rum'],
        }
    
    def _load_model_artifacts(self, model_type: str) -> Dict[str, Any]:
        """Load model artifacts from disk"""
        if model_type in self.loaded_models:
            return self.loaded_models[model_type]
        
        if model_type not in self.model_configs:
            raise ValueError(f"Unknown model type: {model_type}")
        
        artifacts = {}
        config = self.model_configs[model_type]
        base_path = config.get('base_path')
        
        # Skip if no base_path (model not implemented yet)
        if base_path is None:
            self.loaded_models[model_type] = artifacts
            return artifacts
        
        # Handle bundled models (like customer_churn)
        if 'bundle' in config:
            bundle_path = os.path.join(self.models_dir, base_path, config['bundle'])
            if os.path.exists(bundle_path):
                try:
                    bundle = joblib.load(bundle_path)
                    artifacts = bundle if isinstance(bundle, dict) else {'model': bundle}
                except Exception as e:
                    print(f"Warning: Could not load bundle {bundle_path}: {e}")
                    artifacts = {}
            self.loaded_models[model_type] = artifacts
            return artifacts
        
        # Load individual artifacts
        for key, filename in config.items():
            if key == 'base_path':
                continue
            filepath = os.path.join(self.models_dir, base_path, filename)
            if os.path.exists(filepath):
                try:
                    artifacts[key] = joblib.load(filepath)
                except Exception as e:
                    print(f"Warning: Could not load {filepath}: {e}")
                    artifacts[key] = None
            else:
                artifacts[key] = None
        
        self.loaded_models[model_type] = artifacts
        return artifacts
    
    def is_model_available(self, model_type: str) -> bool:
        """Check if a model has been trained and is available"""
        if model_type == 'demand_forecast':
            # Check if XGB models directory exists
            config = self.model_configs.get('demand_forecast', {})
            base_path = config.get('base_path')
            if base_path:
                models_dir = os.path.join(self.models_dir, base_path, config.get('models_subdir', ''))
                return os.path.exists(models_dir) and len(os.listdir(models_dir)) > 0
            return False
        
        artifacts = self._load_model_artifacts(model_type)
        
        # No artifacts loaded
        if not artifacts:
            return False
        
        # Check based on model type
        if model_type == 'campaign_roi':
            return artifacts.get('regressor') is not None
        elif model_type == 'customer_churn':
            # Bundle or model key
            return artifacts.get('model') is not None or len(artifacts) > 0
        else:
            return artifacts.get('model') is not None
    
    # ========================================================================
    # 1. DEMAND & STOCK FORECASTER
    # ========================================================================
    
    def _map_item_to_category(self, item_name: str) -> Optional[str]:
        """
        Map an item name to a trained category model using keyword matching
        
        Args:
            item_name: The item's name/title
            
        Returns:
            Category name if found, None otherwise
        """
        if not item_name:
            return None
            
        item_lower = item_name.lower()
        
        # Check each category's keywords
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in item_lower:
                    return category
        
        return None
    
    def _load_item_forecast_model(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Load item-specific forecast model and scaler"""
        cache_key = item_name
        if cache_key in self.item_forecast_models:
            return self.item_forecast_models[cache_key]
        
        config = self.model_configs.get('demand_forecast', {})
        base_path = config.get('base_path')
        if not base_path:
            return None
        
        # First try exact match
        model_file = f"{item_name}.joblib"
        scaler_file = f"{item_name}_scaler.joblib"
        
        model_path = os.path.join(self.models_dir, base_path, config.get('models_subdir', ''), model_file)
        scaler_path = os.path.join(self.models_dir, base_path, config.get('scalers_subdir', ''), scaler_file)
        
        # If exact match not found, try category mapping
        if not os.path.exists(model_path):
            category = self._map_item_to_category(item_name)
            if category:
                model_file = f"{category}.joblib"
                scaler_file = f"{category}_scaler.joblib"
                model_path = os.path.join(self.models_dir, base_path, config.get('models_subdir', ''), model_file)
                scaler_path = os.path.join(self.models_dir, base_path, config.get('scalers_subdir', ''), scaler_file)
                
                if not os.path.exists(model_path):
                    return None
            else:
                return None
        
        try:
            artifacts = {
                'model': joblib.load(model_path),
                'scaler': joblib.load(scaler_path) if os.path.exists(scaler_path) else None
            }
            self.item_forecast_models[cache_key] = artifacts
            return artifacts
        except Exception as e:
            print(f"Error loading forecast model for {item_name}: {e}")
            return None
    
    def predict_demand(
        self,
        item_id: int,
        forecast_days: int = 7,
        is_holiday: bool = False,
        is_weekend: bool = False,
        campaign_active: bool = False,
        price: Optional[float] = None,
        item_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict demand for an item over the next N days
        
        Args:
            item_id: Item ID to forecast
            forecast_days: Number of days to forecast ahead
            is_holiday: Whether forecast period includes holidays
            is_weekend: Whether forecast period includes weekends
            campaign_active: Whether a campaign will be running
            price: Item price (if None, uses current price)
            item_name: Item name (for loading appropriate model)
        
        Returns:
            Dictionary with forecast data and recommendations
        """
        # Try to load item-specific model
        model_artifacts = None
        if item_name:
            model_artifacts = self._load_item_forecast_model(item_name)
        
        if model_artifacts is None or model_artifacts.get('model') is None:
            # Return fallback with simple average if model not available
            return {
                'status': 'model_not_available',
                'message': f'Demand forecasting model not available for item: {item_name or item_id}',
                'item_id': item_id,
                'forecast_days': forecast_days,
                'predictions': self._generate_fallback_forecast(forecast_days),
                'note': 'Using historical average fallback'
            }
        
        # Prepare future dates
        predictions = []
        for day_offset in range(forecast_days):
            pred_date = datetime.now() + timedelta(days=day_offset + 1)
            
            # Create features for this day
            features = pd.DataFrame([{
                'day_of_week': pred_date.weekday(),
                'month': pred_date.month,
                'day': pred_date.day,
                'is_weekend': int(pred_date.weekday() >= 5),
                'is_holiday': int(is_holiday),
                'campaign_active': int(campaign_active)
            }])
            
            # Scale if scaler available
            if model_artifacts.get('scaler'):
                features_scaled = model_artifacts['scaler'].transform(features)
            else:
                features_scaled = features.values
            
            # Predict
            try:
                quantity = model_artifacts['model'].predict(features_scaled)[0]
            except Exception as e:
                print(f"Prediction error: {e}")
                quantity = 10.0  # Fallback value
            
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'predicted_quantity': max(0, round(float(quantity), 2)),
                'day_of_week': pred_date.strftime('%A'),
                'is_weekend': pred_date.weekday() >= 5
            })
        
        total_predicted = sum(p['predicted_quantity'] for p in predictions)
        
        return {
            'status': 'success',
            'item_id': item_id,
            'forecast_days': forecast_days,
            'predictions': predictions,
            'summary': {
                'total_predicted_demand': round(total_predicted, 2),
                'avg_daily_demand': round(total_predicted / forecast_days, 2),
                'peak_day': max(predictions, key=lambda x: x['predicted_quantity']) if predictions else None
            }
        }
    
    def _generate_fallback_forecast(self, forecast_days: int) -> List[Dict[str, Any]]:
        """Generate simple fallback forecast based on average"""
        predictions = []
        avg_daily = 15.0  # Simple fallback average
        
        for day_offset in range(forecast_days):
            pred_date = datetime.now() + timedelta(days=day_offset + 1)
            # Higher demand on weekends
            multiplier = 1.5 if pred_date.weekday() >= 5 else 1.0
            
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'predicted_quantity': round(avg_daily * multiplier, 2),
                'day_of_week': pred_date.strftime('%A'),
                'is_weekend': pred_date.weekday() >= 5
            })
        
        return predictions
    
    def get_reorder_recommendations(
        self,
        item_id: int,
        current_stock: float,
        lead_time_days: int = 3,
        safety_stock_multiplier: float = 1.2,
        item_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get stock reorder recommendations based on demand forecast
        
        Args:
            item_id: Item ID
            current_stock: Current stock level
            lead_time_days: Days until new stock arrives
            safety_stock_multiplier: Safety stock factor (1.2 = 20% buffer)
            item_name: Item name for model loading
        
        Returns:
            Reorder recommendations
        """
        # Forecast for lead time + 7 days
        forecast_days = lead_time_days + 7
        forecast = self.predict_demand(item_id, forecast_days, item_name=item_name)
        
        if forecast['status'] != 'success' and forecast['status'] != 'model_not_available':
            return forecast
        
        # Calculate needed stock - handle both cases (with and without summary)
        if 'summary' in forecast and 'total_predicted_demand' in forecast['summary']:
            total_demand = forecast['summary']['total_predicted_demand']
        else:
            # Calculate from predictions array if summary not available
            predictions = forecast.get('predictions', [])
            total_demand = sum(p.get('predicted_quantity', 0) for p in predictions)
        
        needed_stock = total_demand * safety_stock_multiplier
        reorder_qty = max(0, needed_stock - current_stock)
        
        # Calculate stockout risk
        days_until_stockout = None
        cumulative_demand = 0
        for pred in forecast.get('predictions', []):
            cumulative_demand += pred['predicted_quantity']
            if cumulative_demand > current_stock:
                days_until_stockout = pred['date']
                break
        
        return {
            'status': 'success',
            'item_id': item_id,
            'current_stock': current_stock,
            'forecast_period_days': forecast_days,
            'predicted_demand': round(total_demand, 2),
            'recommendations': {
                'reorder_needed': reorder_qty > 0,
                'reorder_quantity': round(reorder_qty, 2),
                'urgency': 'high' if days_until_stockout and datetime.strptime(days_until_stockout, '%Y-%m-%d') < datetime.now() + timedelta(days=3) else 'medium' if reorder_qty > 0 else 'low',
                'days_until_stockout': days_until_stockout,
                'safety_stock_level': round(needed_stock, 2)
            }
        }
    
    # ========================================================================
    # 2. CAMPAIGN ROI & REDEMPTION PREDICTOR
    # ========================================================================
    
    def predict_campaign_performance(
        self,
        duration_days: int,
        points: int,
        discount_percent: float,
        minimum_spend: float
    ) -> Dict[str, Any]:
        """
        Predict campaign redemptions and success probability
        
        Args:
            duration_days: Campaign duration in days
            points: Loyalty points offered
            discount_percent: Discount percentage (0-100)
            minimum_spend: Minimum spend requirement in DKK
        
        Returns:
            Campaign performance predictions
        """
        artifacts = self._load_model_artifacts('campaign_roi')
        
        if artifacts['regressor'] is None:
            return {
                'status': 'model_not_ready',
                'message': 'Campaign ROI model not yet trained'
            }
        
        # Prepare features (matches actual trained model features)
        # Use defaults for time-based features (median values from training)
        current_time = datetime.now()
        
        features = {
            'duration_days': duration_days,
            'points': points,
            'discount': discount_percent,
            'minimum_spend': minimum_spend,
            'redemptions': 0,  # Will be predicted, use 0 as placeholder
            'is_percentage_discount': 1,  # Assume percentage discount
            'is_total_bill_discount': 0,  # Assume not total bill
            'is_freebie': 1 if points > 0 and discount_percent == 0 else 0,
            'start_hour': current_time.hour,  # Default to current hour
            'start_day_of_week': current_time.weekday(),  # 0=Monday
            'start_month': current_time.month,
            'is_weekend': 1 if current_time.weekday() >= 5 else 0,
            'discount_per_min_spend': discount_percent / max(minimum_spend, 1),
            'redemptions_per_duration': 0  # Will be predicted
        }
        
        # Convert to DataFrame
        feature_names = artifacts['features']
        X = pd.DataFrame([features])[feature_names]
        
        # Scale features
        X_scaled = artifacts['scaler'].transform(X)
        
        # Predictions
        predicted_redemptions = artifacts['regressor'].predict(X_scaled)[0]
        success_probability = artifacts['classifier'].predict_proba(X_scaled)[0][1]
        
        # Recommendation logic
        if success_probability >= 0.7 and predicted_redemptions >= 20:
            recommendation = "LAUNCH"
            reason = "High success probability with good redemption rate"
        elif success_probability >= 0.5 and predicted_redemptions >= 15:
            recommendation = "LAUNCH WITH MONITORING"
            reason = "Moderate success expected - monitor closely"
        elif success_probability < 0.3:
            recommendation = "REVISE"
            reason = "Low success probability - consider better incentives"
        else:
            recommendation = "TEST SMALL SCALE"
            reason = "Uncertain outcome - test with limited audience first"
        
        return {
            'status': 'success',
            'predictions': {
                'expected_redemptions': round(float(predicted_redemptions), 1),
                'success_probability': round(float(success_probability) * 100, 1),
                'is_successful': bool(success_probability >= 0.5)
            },
            'campaign_details': {
                'duration_days': int(duration_days),
                'points': int(points),
                'discount_percent': float(discount_percent),
                'minimum_spend': float(minimum_spend)
            },
            'recommendation': {
                'action': recommendation,
                'reason': reason,
                'confidence': 'high' if abs(success_probability - 0.5) > 0.3 else 'medium'
            }
        }
    
    def optimize_campaign_parameters(
        self,
        target_redemptions: int = 25,
        max_discount: float = 30,
        budget_per_redemption: float = 100
    ) -> Dict[str, Any]:
        """
        Find optimal campaign parameters to achieve target redemptions
        
        Args:
            target_redemptions: Desired number of redemptions
            max_discount: Maximum allowed discount percentage
            budget_per_redemption: Budget per expected redemption
        
        Returns:
            Optimized campaign parameters
        """
        artifacts = self._load_model_artifacts('campaign_roi')
        
        if artifacts['regressor'] is None:
            return {
                'status': 'model_not_ready',
                'message': 'Campaign ROI model not yet trained'
            }
        
        best_score = -1
        best_params = None
        
        # Grid search over parameter space
        for duration in [3, 7, 14]:
            for points in [100, 200, 300, 500]:
                for discount in [10, 15, 20, 25, 30]:
                    if discount > max_discount:
                        continue
                    for min_spend in [50, 100, 150, 200]:
                        # Predict
                        result = self.predict_campaign_performance(
                            duration, points, discount, min_spend
                        )
                        
                        if result['status'] != 'success':
                            continue
                        
                        pred_redemptions = result['predictions']['expected_redemptions']
                        success_prob = result['predictions']['success_probability']
                        
                        # Score = minimize distance to target while maximizing success prob
                        redemption_score = 1 - abs(pred_redemptions - target_redemptions) / target_redemptions
                        total_score = (redemption_score * 0.6) + (success_prob / 100 * 0.4)
                        
                        if total_score > best_score:
                            best_score = total_score
                            best_params = {
                                'duration_days': duration,
                                'points': points,
                                'discount_percent': discount,
                                'minimum_spend': min_spend,
                                'expected_redemptions': pred_redemptions,
                                'success_probability': success_prob
                            }
        
        return {
            'status': 'success',
            'optimal_parameters': best_params,
            'target_redemptions': target_redemptions,
            'optimization_score': round(best_score, 3)
        }
    
    # ========================================================================
    # 3. CUSTOMER CHURN & LOYALTY SCORER
    # ========================================================================
    
    def predict_customer_churn(
        self,
        customer_id: int,
        recent_waiting_time: float,
        recent_rating: float,
        points_redeemed: int,
        vip_threshold: float,
        days_since_last_order: int
    ) -> Dict[str, Any]:
        """
        Predict customer churn probability
        
        Args:
            customer_id: Customer ID
            recent_waiting_time: Average waiting time (minutes)
            recent_rating: Recent order rating (1-5)
            points_redeemed: Total points redeemed
            vip_threshold: VIP threshold for this customer
            days_since_last_order: Days since last order
        
        Returns:
            Churn prediction and retention recommendations
        """
        artifacts = self._load_model_artifacts('customer_churn')
        
        if not artifacts or 'model' not in artifacts:
            return {
                'status': 'model_not_ready',
                'message': 'Customer churn model not yet trained'
            }
        
        # Prepare features - use common customer churn features
        features = pd.DataFrame([{
            'waiting_time_avg': recent_waiting_time,
            'rating_avg': recent_rating,
            'points_redeemed_total': points_redeemed,
            'vip_threshold': vip_threshold,
            'days_since_last_order': days_since_last_order,
            'is_vip': int(points_redeemed >= vip_threshold),
            'satisfaction_score': recent_rating - (recent_waiting_time / 10),
            'engagement_score': points_redeemed / max(days_since_last_order, 1)
        }])
        
        # Try to get feature names from artifacts
        if 'features' in artifacts and artifacts['features'] is not None:
            try:
                # Reorder features to match training
                feature_names = artifacts['features']
                features = features[[col for col in feature_names if col in features.columns]]
            except:
                pass  # Use features as is
        
        # Scale and predict
        try:
            if 'scaler' in artifacts and artifacts['scaler'] is not None:
                X_scaled = artifacts['scaler'].transform(features)
            else:
                X_scaled = features.values
            
            model = artifacts['model']
            if hasattr(model, 'predict_proba'):
                churn_probability = model.predict_proba(X_scaled)[0][1]
            else:
                churn_probability = float(model.predict(X_scaled)[0])
        except Exception as e:
            return {
                'status': 'prediction_error',
                'message': f'Error during prediction: {str(e)}'
            }
        
        # Retention recommendations
        if churn_probability >= 0.7:
            urgency = 'critical'
            actions = [
                'Send immediate SMS offer with 25% discount',
                'Assign dedicated customer service representative',
                'Offer VIP benefits upgrade'
            ]
        elif churn_probability >= 0.4:
            urgency = 'high'
            actions = [
                'Send personalized email with 15% discount',
                'Bonus points reward on next order',
                'Request feedback survey with incentive'
            ]
        else:
            urgency = 'low'
            actions = [
                'Include in regular loyalty program communications',
                'Monthly newsletter with special offers'
            ]
        
        return {
            'status': 'success',
            'customer_id': customer_id,
            'churn_risk': {
                'probability': round(churn_probability * 100, 1),
                'level': urgency,
                'will_churn': churn_probability >= 0.5
            },
            'retention_strategy': {
                'urgency': urgency,
                'recommended_actions': actions,
                'estimated_retention_cost': 50 if urgency == 'critical' else 25 if urgency == 'high' else 10
            },
            'customer_insights': {
                'satisfaction_score': round(recent_rating - (recent_waiting_time / 10), 2),
                'engagement_level': 'high' if (points_redeemed / max(days_since_last_order, 1)) > 10 else 'medium' if (points_redeemed / max(days_since_last_order, 1)) > 5 else 'low',
                'is_vip': bool(points_redeemed >= vip_threshold)
            }
        }
    
    # ========================================================================
    # 4. OPERATIONAL RISK & CASHIER INTEGRITY MONITOR
    # ========================================================================
    
    def detect_cashier_anomalies(
        self,
        cashier_id: int,
        shift_date: str,
        order_count: int,
        expected_balance: float,
        actual_balance: float,
        total_vat: float,
        avg_order_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Detect anomalous cashier behavior or operational risks
        
        Args:
            cashier_id: Cashier/user ID
            shift_date: Shift date (YYYY-MM-DD)
            order_count: Number of orders processed
            expected_balance: Expected cash balance
            actual_balance: Actual cash balance
            total_vat: Total VAT collected
            avg_order_value: Average order value
        
        Returns:
            Anomaly detection results and risk assessment
        """
        artifacts = self._load_model_artifacts('cashier_risk')
        
        if artifacts['model'] is None:
            return {
                'status': 'model_not_ready',
                'message': 'Cashier risk model not yet trained'
            }
        
        # Calculate features
        balance_difference = expected_balance - actual_balance
        balance_discrepancy_pct = (balance_difference / max(expected_balance, 1)) * 100
        
        if avg_order_value is None:
            avg_order_value = expected_balance / max(order_count, 1)
        
        features = {
            'order_count': order_count,
            'balance_difference': abs(balance_difference),
            'balance_discrepancy_pct': abs(balance_discrepancy_pct),
            'total_vat': total_vat,
            'avg_order_value': avg_order_value,
            'vat_to_balance_ratio': total_vat / max(expected_balance, 1),
            'orders_per_hour': order_count / 8  # Assuming 8-hour shift
        }
        
        # Convert to DataFrame
        feature_names = artifacts['features']
        X = pd.DataFrame([features])[feature_names]
        
        # Scale and predict
        X_scaled = artifacts['scaler'].transform(X)
        risk_score = artifacts['model'].predict(X_scaled)[0]
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = 'critical'
            alert_type = 'immediate_investigation'
            recommended_actions = [
                'Immediate supervisor review required',
                'Audit all transactions from this shift',
                'Interview cashier and witnesses',
                'Review security camera footage'
            ]
        elif risk_score >= 0.5:
            risk_level = 'high'
            alert_type = 'flagged_for_review'
            recommended_actions = [
                'Manager review within 24 hours',
                'Compare with historical patterns',
                'Review transaction logs'
            ]
        elif risk_score >= 0.3:
            risk_level = 'medium'
            alert_type = 'monitoring'
            recommended_actions = [
                'Add to weekly audit sample',
                'Monitor future shifts'
            ]
        else:
            risk_level = 'low'
            alert_type = 'normal_operations'
            recommended_actions = ['No action required']
        
        return {
            'status': 'success',
            'cashier_id': cashier_id,
            'shift_date': shift_date,
            'risk_assessment': {
                'risk_score': round(risk_score, 3),
                'risk_level': risk_level,
                'alert_type': alert_type,
                'requires_action': risk_level in ['critical', 'high']
            },
            'financial_metrics': {
                'expected_balance': round(expected_balance, 2),
                'actual_balance': round(actual_balance, 2),
                'difference': round(balance_difference, 2),
                'discrepancy_percent': round(balance_discrepancy_pct, 2),
                'total_vat': round(total_vat, 2)
            },
            'operational_metrics': {
                'order_count': order_count,
                'avg_order_value': round(avg_order_value, 2),
                'orders_per_hour': round(features['orders_per_hour'], 2)
            },
            'recommended_actions': recommended_actions
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_available_models(self) -> Dict[str, bool]:
        """Get status of all available models"""
        return {
            'demand_forecast': self.is_model_available('demand_forecast'),
            'campaign_roi': self.is_model_available('campaign_roi'),
            'customer_churn': self.is_model_available('customer_churn'),
            'cashier_risk': self.is_model_available('cashier_risk')
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for ML service"""
        available_models = self.get_available_models()
        
        return {
            'service': 'ML Prediction Service',
            'status': 'healthy',
            'models_available': available_models,
            'total_models': len(available_models),
            'ready_models': sum(available_models.values()),
            'models_directory': self.models_dir
        }
