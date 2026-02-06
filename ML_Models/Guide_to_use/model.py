import joblib
import os
import numpy as np
import pandas as pd
def date_to_features(date, holidays= [
    '2023-01-01', '2023-02-21', '2023-03-30', '2023-04-10', '2023-05-01',
    '2023-06-12', '2023-12-25', '2024-01-01', '2024-02-10', '2024-03-30',
    '2024-05-01', '2024-12-25']):
    """
    Transforms a date to day_of_week, is_weekend, is_holiday, month.
    Args:
        date (str or pd.Timestamp): Date to transform.
        holidays (list of str or pd.Timestamp): List of holiday dates.
    Returns:
        day_of_week (int): Monday=0, Sunday=6
        is_weekend (int): 1 if Saturday/Sunday, else 0
        is_holiday (int): 1 if date is in holidays, else 0
        month (int): Month number
    """
    dt = pd.to_datetime(date)
    day_of_week = dt.dayofweek
    is_weekend = 1 if day_of_week in [5, 6] else 0
    month = dt.month
    is_holiday = 0
    if holidays is not None:
        holidays = [pd.to_datetime(h).date() for h in holidays]
        if dt.date() in holidays:
            is_holiday = 1
    return day_of_week, is_weekend, is_holiday, month
class StockForecaster:
    """
    Forecasts next day's stock quantity for a given item using per-item XGBoost models.
    Features: day_of_week, is_weekend, is_holiday, month, last_qty (scaled)
    """
    def __init__(self):
        self.model_dir = "D:/Deloitte/DIH-X-AUC-Hackathon/ML_Models/stock_forecaster/models/xgb_models/"
        self.scaler_dir = "D:/Deloitte/DIH-X-AUC-Hackathon/ML_Models/stock_forecaster/models/scalers/"
        self.items = [f.split('.joblib')[0] for f in os.listdir(self.model_dir) if f.endswith('.joblib')]
    def predict(self, item_name, day_of_week, is_weekend, is_holiday, month, last_qty):
        model_path = os.path.join(self.model_dir, f"{item_name}.joblib")
        scaler_path = os.path.join(self.scaler_dir, f"{item_name}_scaler.joblib")
        if not os.path.exists(model_path):
            raise ValueError(f"Model for item '{item_name}' not found.")
        model = joblib.load(model_path)
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            qty_scaled = float(scaler.transform([[last_qty]])[0][0])
        else:
            qty_scaled = last_qty
        features = np.array([[day_of_week, is_weekend, is_holiday, month, qty_scaled]])
        prediction = float(model.predict(features)[0])
        prediction = max(0, prediction)
        return prediction
class Customer_Churn_Detection: #check if they will lose interest or not
    def __init__(self):
        file_path = "D:/Deloitte/DIH-X-AUC-Hackathon/ML_Models/customer_churn/model_bundle.joblib"
        bundle = joblib.load(file_path)
        self.model = bundle["model"]
        self.scaler = bundle["scaler"]
    def predict(self,discount_amount,points_earned,price,waiting_time):
        x = [[discount_amount,points_earned,price,waiting_time]]
        x_s = self.scaler.transform(x)
        y = self.model.predict(x_s)
        return y[0]
class Campaign_Detector: #
    def __init__(self):
        model_dir = "D:/Deloitte/DIH-X-AUC-Hackathon/ML_Models/Campaign_ROI_Predictor/models/"
        self.regressor = joblib.load(os.path.join(model_dir, 'campaign_redemption_regressor.pkl'))
        self.classifier = joblib.load(os.path.join(model_dir, 'campaign_success_classifier.pkl'))
        self.scaler = joblib.load(os.path.join(model_dir, 'campaign_scaler.pkl'))
        self.feature_columns = joblib.load(os.path.join(model_dir, 'campaign_features.pkl'))
    def predict_redemption(self,duration_days,points,discount,minimum_spend,max_redemptions,is_percentage,
        is_total_bill,is_freebie,start_hour,start_day_of_week,start_month_of_week,is_weekend,
        discount_per_min_spend,redemptions_per_duration):
        x = [[duration_days,points,discount,minimum_spend,max_redemptions,is_percentage,
        is_total_bill,is_freebie,start_hour,start_day_of_week,start_month_of_week,is_weekend,
        discount_per_min_spend,redemptions_per_duration]]
        x_s = self.scaler.transform(x)
        y = self.regressor.predict(x)
        return y[0]
    def predict_success_probability(self,duration_days,points,discount,minimum_spend,max_redemptions,is_percentage,
        is_total_bill,is_freebie,start_hour,start_day_of_week,start_month_of_week,is_weekend,
        discount_per_min_spend,redemptions_per_duration):
        x = [[duration_days,points,discount,minimum_spend,max_redemptions,is_percentage,
        is_total_bill,is_freebie,start_hour,start_day_of_week,start_month_of_week,is_weekend,
        discount_per_min_spend,redemptions_per_duration]]
        x_s = self.scaler.transform(x)
        y = self.classifier.predict_proba(x)
        return y[0][1]

class Customer_Churn_Detection: #check if they will lose interest or not
    def __init__(self):
        file_path = "D:/Deloitte/DIH-X-AUC-Hackathon/ML_Models/customer_churn/model_bundle.joblib"
        bundle = joblib.load(file_path)
        self.model = bundle["model"]
        self.scaler = bundle["scaler"]
    def predict(self,discount_amount,points_earned,price,waiting_time):
        x = [[discount_amount,points_earned,price,waiting_time]]
        x_s = self.scaler.transform(x)
        y = self.model.predict(x_s)
        return y[0]
class Operational_risk_predictor: #calculate percentage of risk for the cashier
    def __init__(self):
        model_dir = "D:/Deloitte/DIH-X-AUC-Hackathon/ML_Models/Operational_risk_predictors/models/"
        self.model = joblib.load(os.path.join(model_dir, 'random_forest_model(preferred).pkl'))
        self.scaler = joblib.load(os.path.join(model_dir, 'feature_scaler.pkl'))
        self.feature_columns = joblib.load(os.path.join(model_dir, 'feature_columns.pkl'))
        print(self.feature_columns)
    def predict_risk_percentage(self,balance_diff_sum, balance_diff_mean, balance_diff_std, balance_diff_min, balance_diff_max,
                                 balance_discrepancy_pct_mean, balance_discrepancy_pct_max, transaction_total_sum,
                                   transaction_total_count, transaction_total_mean, vat_component_sum, num_transactions_sum,
                                     opening_balance_mean,closing_balance_mean, id_count, total_amount_sum, total_amount_mean,
                                       total_amount_std, cash_amount_sum, cash_amount_mean):
        x = [[balance_diff_sum, balance_diff_mean, balance_diff_std, balance_diff_min, balance_diff_max,
                                 balance_discrepancy_pct_mean, balance_discrepancy_pct_max, transaction_total_sum,
                                   transaction_total_count, transaction_total_mean, vat_component_sum, num_transactions_sum,
                                     opening_balance_mean,closing_balance_mean, id_count, total_amount_sum, total_amount_mean,
                                       total_amount_std, cash_amount_sum, cash_amount_mean]]
        x_s = self.scaler.transform(x)
        y = self.model.predict_proba(x)
        return y[0][1]
class RevenuePredictor:
    """
    Predicts next day's revenue using XGBRegressor model.
    Features: is_weekend, is_holiday, lagged_revenue
    """
    def __init__(self):
        self.model_path = "D:/Deloitte/DIH-X-AUC-Hackathon/ML_Models/revenue_predictor/revenue_predictor_xgb.pkl"
        self.model = joblib.load(self.model_path)
        self.feature_names = ["is_weekend", "is_holiday", "lagged_revenue"]
        # Optionally load metadata
        self.metadata_path = "D:/Deloitte/DIH-X-AUC-Hackathon/ML_Models/revenue_predictor/revenue_predictor_metadata.json"
        if os.path.exists(self.metadata_path):
            import json
            with open(self.metadata_path, "r") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = None
    def predict(self, is_weekend, is_holiday, lagged_revenue):
        import numpy as np
        features = np.array([[is_weekend, is_holiday, lagged_revenue]])
        prediction = float(self.model.predict(features)[0])
        prediction = max(0, prediction)
        return prediction
