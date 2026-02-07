import joblib
import os
import numpy as np
import pandas as pd
import json

def date_to_features(date):
    """
    Transforms a date to month feature.
    Args:
        date (str or pd.Timestamp): Date to transform.
    Returns:
        month (int): Month number
    """
    dt = pd.to_datetime(date)
    month = dt.month
    return month

class StockForecaster:
    """
    Forecasts next day's stock quantity for a given category using XGBoost models.
    Features: month, last_qty (scaled)
    NOTE: Updated to use category-based models instead of item-specific models for better accuracy.
    """
    def __init__(self, models_dir="ML_Models/stock_forecaster"):
        self.model_dir = os.path.join(models_dir, "models/xgb_models/")
        self.scaler_dir = os.path.join(models_dir, "models/scalers/")
        
        # Cache for loaded models and scalers
        self.model_cache = {}
        self.scaler_cache = {}
        
        # Load MSE metrics
        mse_path = os.path.join(models_dir, "MSE.json")
        if os.path.exists(mse_path):
            with open(mse_path, 'r', encoding='utf-8') as f:
                self.errors = json.load(f)
        else:
            self.errors = {}
        
        # Available categories
        if os.path.exists(self.model_dir):
            self.categories = [f.split('.joblib')[0] for f in os.listdir(self.model_dir) if f.endswith('.joblib')]
        else:
            self.categories = []
    
    def get_mean_absolute_error(self, category_name):
        """Get the MAE for a category"""
        return self.errors.get(category_name, None)
    
    def predict(self, category_name, month, last_qty, day_of_week=None, is_weekend=None, is_holiday=None):
        """
        Predict demand for a category (supports both 2-feature and 5-feature models)
        Args:
            category_name: Category name (e.g., 'Beverages', 'Handhelds', 'Sodavand')
            month: Month number (1-12)
            last_qty: Last known quantity
            day_of_week: Day of week (0-6, Monday=0) - optional, defaults to current day
            is_weekend: Whether it's weekend (0 or 1) - optional, auto-calculated if not provided
            is_holiday: Whether it's holiday (0 or 1) - optional, defaults to 0
        Returns:
            Predicted quantity (non-negative)
        """
        # Load model and scaler if not cached
        if category_name not in self.model_cache:
            model_path = os.path.join(self.model_dir, f"{category_name}.joblib")
            scaler_path = os.path.join(self.scaler_dir, f"{category_name}_scaler.joblib")
            
            if not os.path.exists(model_path):
                raise ValueError(f"Model for category '{category_name}' not found. Available: {self.categories}")
            
            self.model_cache[category_name] = joblib.load(model_path)
            
            if os.path.exists(scaler_path):
                self.scaler_cache[category_name] = joblib.load(scaler_path)
            else:
                self.scaler_cache[category_name] = None
        
        model = self.model_cache[category_name]
        scaler = self.scaler_cache[category_name]
        
        # Detect model feature count
        n_features = model.n_features_in_ if hasattr(model, 'n_features_in_') else 5
        
        # Scale quantity if scaler exists
        if scaler:
            qty_scaled = float(scaler.transform([[last_qty]])[0][0])
        else:
            qty_scaled = last_qty
        
        if n_features == 2:
            # Old format: [month, qty_scaled]
            features = np.array([[month, qty_scaled]])
        else:
            # New format (5 features): [day_of_week, is_weekend, is_holiday, month, qty_scaled]
            # Auto-calculate day_of_week if not provided
            if day_of_week is None:
                from datetime import datetime
                day_of_week = datetime.now().weekday()
            
            # Auto-calculate is_weekend if not provided
            if is_weekend is None:
                is_weekend = 1 if day_of_week >= 5 else 0
            
            # Default is_holiday to 0 if not provided
            if is_holiday is None:
                is_holiday = 0
            
            features = np.array([[day_of_week, is_weekend, is_holiday, month, qty_scaled]])
        
        # Predict
        prediction = float(model.predict(features)[0])
        prediction = max(0, prediction)
        
        return prediction

class Customer_Churn_Detection:
    """Check if customer will lose interest or not"""
    def __init__(self, models_dir="ML_Models"):
        file_path = os.path.join(models_dir, "customer_churn/model_bundle.joblib")
        bundle = joblib.load(file_path)
        self.model = bundle["model"]
        self.scaler = bundle["scaler"]
    
    def predict(self, discount_amount, points_earned, price, waiting_time):
        """
        Predict customer churn
        Args:
            discount_amount: Total discount amount received
            points_earned: Total points earned
            price: Average order price
            waiting_time: Average waiting time
        Returns:
            1 if customer will churn, 0 otherwise
        """
        x = [[discount_amount, points_earned, price, waiting_time]]
        x_s = self.scaler.transform(x)
        y = self.model.predict(x_s)
        return y[0]

class Campaign_Detector:
    """Campaign ROI & Redemption Predictor"""
    def __init__(self, models_dir="ML_Models"):
        model_dir = os.path.join(models_dir, "Campaign_ROI_Predictor/models/")
        self.regressor = joblib.load(os.path.join(model_dir, 'campaign_redemption_regressor.pkl'))
        self.classifier = joblib.load(os.path.join(model_dir, 'campaign_success_classifier.pkl'))
        self.scaler = joblib.load(os.path.join(model_dir, 'campaign_scaler.pkl'))
        self.feature_columns = joblib.load(os.path.join(model_dir, 'campaign_features.pkl'))
    
    def predict_redemption(self, duration_days, points, discount, minimum_spend, max_redemptions, is_percentage,
        is_total_bill, is_freebie, start_hour, start_day_of_week, start_month_of_week, is_weekend,
        discount_per_min_spend, redemptions_per_duration):
        """Predict number of redemptions for a campaign"""
        x = [[duration_days, points, discount, minimum_spend, max_redemptions, is_percentage,
        is_total_bill, is_freebie, start_hour, start_day_of_week, start_month_of_week, is_weekend,
        discount_per_min_spend, redemptions_per_duration]]
        x_s = self.scaler.transform(x)
        y = self.regressor.predict(x_s)
        return y[0]
    
    def predict_success_probability(self, duration_days, points, discount, minimum_spend, max_redemptions, is_percentage,
        is_total_bill, is_freebie, start_hour, start_day_of_week, start_month_of_week, is_weekend,
        discount_per_min_spend, redemptions_per_duration):
        """Predict probability of campaign success"""
        x = [[duration_days, points, discount, minimum_spend, max_redemptions, is_percentage,
        is_total_bill, is_freebie, start_hour, start_day_of_week, start_month_of_week, is_weekend,
        discount_per_min_spend, redemptions_per_duration]]
        x_s = self.scaler.transform(x)
        y = self.classifier.predict_proba(x_s)
        return y[0][1]

class Operational_risk_predictor:
    """Calculate percentage of risk for the cashier"""
    def __init__(self, models_dir="ML_Models"):
        model_dir = os.path.join(models_dir, "Operational_risk_predictors/models/")
        self.model = joblib.load(os.path.join(model_dir, 'random_forest_model(preferred).pkl'))
        self.scaler = joblib.load(os.path.join(model_dir, 'feature_scaler.pkl'))
        self.feature_columns = joblib.load(os.path.join(model_dir, 'feature_columns.pkl'))
    
    def predict_risk_percentage(self, balance_diff_sum, balance_diff_mean, balance_diff_std, balance_diff_min, balance_diff_max,
                                 balance_discrepancy_pct_mean, balance_discrepancy_pct_max, transaction_total_sum,
                                   transaction_total_count, transaction_total_mean, vat_component_sum, num_transactions_sum,
                                     opening_balance_mean, closing_balance_mean, id_count, total_amount_sum, total_amount_mean,
                                       total_amount_std, cash_amount_sum, cash_amount_mean):
        """
        Predict cashier operational risk
        Args:
            All 20 aggregated cashier statistics features
        Returns:
            Risk probability (0-1)
        """
        x = [[balance_diff_sum, balance_diff_mean, balance_diff_std, balance_diff_min, balance_diff_max,
                                 balance_discrepancy_pct_mean, balance_discrepancy_pct_max, transaction_total_sum,
                                   transaction_total_count, transaction_total_mean, vat_component_sum, num_transactions_sum,
                                     opening_balance_mean, closing_balance_mean, id_count, total_amount_sum, total_amount_mean,
                                       total_amount_std, cash_amount_sum, cash_amount_mean]]
        x_s = self.scaler.transform(x)
        y = self.model.predict_proba(x_s)
        return y[0][1]

class RevenuePredictor:
    """
    Predicts next day's revenue using XGBRegressor model.
    Features: is_weekend, is_holiday, lagged_revenue
    """
    def __init__(self, models_dir="ML_Models"):
        self.model_path = os.path.join(models_dir, "revenue_predictor/revenue_predictor_xgb.pkl")
        self.model = joblib.load(self.model_path)
        self.feature_names = ["is_weekend", "is_holiday", "lagged_revenue"]
        
        # Load metadata
        self.metadata_path = os.path.join(models_dir, "revenue_predictor/revenue_predictor_metadata.json")
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = None
    
    def predict(self, is_weekend, is_holiday, lagged_revenue):
        """
        Predict revenue
        Args:
            is_weekend: 1 if weekend, 0 otherwise
            is_holiday: 1 if holiday, 0 otherwise
            lagged_revenue: Previous day's revenue
        Returns:
            Predicted revenue (non-negative)
        """
        features = np.array([[is_weekend, is_holiday, lagged_revenue]])
        prediction = float(self.model.predict(features)[0])
        prediction = max(0, prediction)
        return prediction

# Example usage
if __name__ == '__main__':
    # Test Stock Forecaster
    print("=" * 60)
    print("STOCK FORECASTER - Category-based Model")
    print("=" * 60)
    stock_model = StockForecaster()
    print("Available categories:", stock_model.categories)
    print("\nExample predictions:")
    if "Beverages" in stock_model.categories:
        print("Beverages (month=1, qty=100):", stock_model.predict("Beverages", 1, 100))
        print("MAE for Beverages:", stock_model.get_mean_absolute_error("Beverages"))
    
    print("\n" + "=" * 60)
    print("All ML Models Loaded Successfully!")
    print("=" * 60)
