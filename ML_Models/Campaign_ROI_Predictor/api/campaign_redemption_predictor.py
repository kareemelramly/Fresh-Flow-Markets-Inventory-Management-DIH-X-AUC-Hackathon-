"""
Campaign ROI & Redemption Predictor
====================================

Predictive model to forecast campaign success and redemption frequency.

Independent Variables:
- Duration of bonus code
- Number of points
- Discount amount
- Minimum spend (min_spend)

Dependent Variable:
- Redemptions frequency or used_redemptions per campaign
- Success probability (binary: successful if used_redemptions > threshold)

Models:
1. Regression: Predict number of redemptions
2. Classification: Predict campaign success probability
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    mean_squared_error, r2_score, mean_absolute_error,
    classification_report, confusion_matrix, roc_auc_score, roc_curve
)
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class CampaignRedemptionPredictor:
    """Predict campaign redemption success and frequency."""
    
    def __init__(self, data_path='../../data/Inventory Management/'):
        """Initialize the predictor with data path."""
        self.data_path = data_path
        self.campaign_data = None
        self.model_regression = None
        self.model_classification = None
        self.scaler = None
        self.feature_columns = None
        self.results = {}
        
    def load_and_prepare_data(self):
        """Load and merge campaign-related datasets."""
        print("="*80)
        print("LOADING DATA")
        print("="*80)
        
        # Load campaigns and bonus codes
        campaigns = pd.read_csv(self.data_path + 'fct_campaigns.csv')
        bonus_codes = pd.read_csv(self.data_path + 'fct_bonus_codes.csv')
        
        print(f"\n✅ Loaded {len(campaigns):,} campaigns")
        print(f"✅ Loaded {len(bonus_codes):,} bonus codes")
        
        # Convert dates
        campaigns['start_date_time'] = pd.to_datetime(campaigns['start_date_time'])
        campaigns['end_date_time'] = pd.to_datetime(campaigns['end_date_time'])
        
        # Calculate campaign duration in days
        campaigns['duration_days'] = (
            campaigns['end_date_time'] - campaigns['start_date_time']
        ).dt.total_seconds() / 86400
        
        # Extract points from bonus codes (aggregate by campaign if needed)
        bonus_codes_agg = bonus_codes.groupby('id').agg({
            'points': 'mean',
            'duration': 'first'
        }).reset_index()
        
        # Merge datasets
        self.campaign_data = campaigns.copy()
        
        # Handle missing values in key columns
        self.campaign_data['discount'] = self.campaign_data['discount'].fillna(0)
        self.campaign_data['minimum_spend'] = self.campaign_data['minimum_spend'].fillna(0)
        self.campaign_data['used_redemptions'] = self.campaign_data['used_redemptions'].fillna(0)
        self.campaign_data['redemptions'] = self.campaign_data['redemptions'].fillna(0)
        
        # Add points column (for now using average, can be enriched with actual mapping)
        # For this version, we'll use campaign-level features
        self.campaign_data['points'] = 0  # Placeholder - will be populated from bonus codes if linked
        
        print(f"\n✅ Prepared dataset with {len(self.campaign_data):,} campaigns")
        
        return self.campaign_data
    
    def engineer_features(self):
        """Create additional features for prediction."""
        print("\n" + "="*80)
        print("FEATURE ENGINEERING")
        print("="*80)
        
        df = self.campaign_data.copy()
        
        # Calculate redemption metrics
        df['redemption_rate'] = np.where(
            df['redemptions'] > 0,
            (df['used_redemptions'] / df['redemptions']) * 100,
            0
        )
        
        df['redemptions_per_day'] = np.where(
            df['duration_days'] > 0,
            df['used_redemptions'] / df['duration_days'],
            0
        )
        
        # Binary success indicator (campaign was used)
        df['is_successful'] = (df['used_redemptions'] > 0).astype(int)
        
        # Campaign type encoding
        df['is_percentage_discount'] = (df['discount_type'] != 'Fixed amount').astype(int)
        df['is_total_bill_discount'] = (df['type'] == 'Discount on total bill').astype(int)
        
        # Time-based features
        df['start_hour'] = df['start_date_time'].dt.hour
        df['start_day_of_week'] = df['start_date_time'].dt.dayofweek
        df['start_month'] = df['start_date_time'].dt.month
        
        # Interaction features
        df['discount_per_min_spend'] = np.where(
            df['minimum_spend'] > 0,
            df['discount'] / df['minimum_spend'],
            0
        )
        
        print(f"\n✅ Engineered {len(df.columns)} total features")
        print("\nKey Features Created:")
        print("  • redemption_rate")
        print("  • redemptions_per_day")
        print("  • is_successful (target for classification)")
        print("  • Campaign type indicators")
        print("  • Temporal features")
        print("  • Interaction terms")
        
        self.campaign_data = df
        return df
    
    def prepare_training_data(self, target='used_redemptions', test_size=0.2, random_state=42):
        """Prepare features and target for model training."""
        print("\n" + "="*80)
        print("PREPARING TRAINING DATA")
        print("="*80)
        
        # Define feature columns (Independent Variables)
        self.feature_columns = [
            'duration_days',      # Duration of bonus code
            'points',             # Number of points
            'discount',           # Discount amount
            'minimum_spend',      # Offer details (min_spend)
            'redemptions',        # Max redemptions available
            'is_percentage_discount',
            'is_total_bill_discount',
            'start_hour',
            'start_day_of_week',
            'start_month',
            'discount_per_min_spend'
        ]
        
        # Remove rows with missing target
        df = self.campaign_data.dropna(subset=[target])
        df = df[df[self.feature_columns].notna().all(axis=1)]
        
        # Prepare features and target
        X = df[self.feature_columns]
        y = df[target]
        
        print(f"\n✅ Dataset prepared:")
        print(f"   • {len(X):,} samples")
        print(f"   • {len(self.feature_columns)} features")
        print(f"   • Target: {target}")
        print(f"\nTarget Statistics:")
        print(f"   • Mean: {y.mean():.2f}")
        print(f"   • Median: {y.median():.2f}")
        print(f"   • Std: {y.std():.2f}")
        print(f"   • Min: {y.min():.2f}")
        print(f"   • Max: {y.max():.2f}")
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"\n✅ Train-Test Split:")
        print(f"   • Training: {len(X_train):,} samples ({(1-test_size)*100:.0f}%)")
        print(f"   • Testing: {len(X_test):,} samples ({test_size*100:.0f}%)")
        
        return X_train_scaled, X_test_scaled, y_train, y_test, X_train, X_test
    
    def train_regression_models(self, X_train, X_test, y_train, y_test):
        """Train regression models to predict redemption count."""
        print("\n" + "="*80)
        print("TRAINING REGRESSION MODELS")
        print("="*80)
        
        models = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        self.results['regression'] = {}
        
        for name, model in models.items():
            print(f"\n🔄 Training {name}...")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Metrics
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            test_mae = mean_absolute_error(y_test, y_pred_test)
            
            self.results['regression'][name] = {
                'model': model,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'test_mae': test_mae,
                'predictions': y_pred_test
            }
            
            print(f"   ✅ Train R²: {train_r2:.4f}")
            print(f"   ✅ Test R²: {test_r2:.4f}")
            print(f"   ✅ Test RMSE: {test_rmse:.4f}")
            print(f"   ✅ Test MAE: {test_mae:.4f}")
        
        # Select best model
        best_model_name = max(
            self.results['regression'],
            key=lambda k: self.results['regression'][k]['test_r2']
        )
        self.model_regression = self.results['regression'][best_model_name]['model']
        
        print(f"\n🏆 Best Model: {best_model_name}")
        print(f"   R² Score: {self.results['regression'][best_model_name]['test_r2']:.4f}")
        
        return self.results['regression']
    
    def train_classification_models(self, X_train, X_test, y_train, y_test):
        """Train classification models to predict campaign success."""
        print("\n" + "="*80)
        print("TRAINING CLASSIFICATION MODELS")
        print("="*80)
        
        # Create binary target (successful = used_redemptions > 0)
        y_train_binary = (y_train > 0).astype(int)
        y_test_binary = (y_test > 0).astype(int)
        
        print(f"\nSuccess Rate:")
        print(f"   • Training: {y_train_binary.mean()*100:.2f}%")
        print(f"   • Testing: {y_test_binary.mean()*100:.2f}%")
        
        models = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        }
        
        self.results['classification'] = {}
        
        for name, model in models.items():
            print(f"\n🔄 Training {name}...")
            
            # Train model
            model.fit(X_train, y_train_binary)
            
            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Metrics
            train_acc = (y_pred_train == y_train_binary).mean()
            test_acc = (y_pred_test == y_test_binary).mean()
            
            try:
                auc = roc_auc_score(y_test_binary, y_pred_proba)
            except:
                auc = None
            
            self.results['classification'][name] = {
                'model': model,
                'train_accuracy': train_acc,
                'test_accuracy': test_acc,
                'auc': auc,
                'predictions': y_pred_test,
                'probabilities': y_pred_proba,
                'y_test': y_test_binary
            }
            
            print(f"   ✅ Train Accuracy: {train_acc:.4f}")
            print(f"   ✅ Test Accuracy: {test_acc:.4f}")
            if auc:
                print(f"   ✅ AUC-ROC: {auc:.4f}")
        
        # Select best model
        best_model_name = max(
            self.results['classification'],
            key=lambda k: self.results['classification'][k]['test_accuracy']
        )
        self.model_classification = self.results['classification'][best_model_name]['model']
        
        print(f"\n🏆 Best Model: {best_model_name}")
        print(f"   Accuracy: {self.results['classification'][best_model_name]['test_accuracy']:.4f}")
        
        return self.results['classification']
    
    def analyze_feature_importance(self, X_train_original):
        """Analyze which features are most important for predictions."""
        print("\n" + "="*80)
        print("FEATURE IMPORTANCE ANALYSIS")
        print("="*80)
        
        # Get feature importance from Random Forest models
        if 'Random Forest' in self.results['regression']:
            rf_reg = self.results['regression']['Random Forest']['model']
            importance_df = pd.DataFrame({
                'Feature': self.feature_columns,
                'Importance': rf_reg.feature_importances_
            }).sort_values('Importance', ascending=False)
            
            print("\n📊 Top Features for Redemption Prediction:")
            for idx, row in importance_df.head(10).iterrows():
                print(f"   {row['Feature']:30s} {row['Importance']:.4f}")
            
            self.results['feature_importance'] = importance_df
            
            return importance_df
    
    def predict_campaign_success(self, campaign_params):
        """
        Predict campaign success for new campaigns.
        
        Parameters:
        -----------
        campaign_params : dict
            Dictionary with keys: duration_days, points, discount, minimum_spend, etc.
        
        Returns:
        --------
        dict : Predictions including redemption count and success probability
        """
        # Prepare input
        input_df = pd.DataFrame([campaign_params])
        
        # Ensure all features are present
        for col in self.feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        
        input_df = input_df[self.feature_columns]
        input_scaled = self.scaler.transform(input_df)
        
        # Predictions
        redemptions_pred = self.model_regression.predict(input_scaled)[0]
        success_prob = self.model_classification.predict_proba(input_scaled)[0, 1]
        
        return {
            'predicted_redemptions': max(0, redemptions_pred),
            'success_probability': success_prob,
            'is_recommended': success_prob > 0.5 and redemptions_pred > 5
        }
    
    def save_models(self, output_dir='../../models/'):
        """Save trained models and scaler."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save models
        joblib.dump(self.model_regression, output_dir + 'campaign_regression_model.pkl')
        joblib.dump(self.model_classification, output_dir + 'campaign_classification_model.pkl')
        joblib.dump(self.scaler, output_dir + 'campaign_scaler.pkl')
        joblib.dump(self.feature_columns, output_dir + 'campaign_features.pkl')
        
        print(f"\n✅ Models saved to {output_dir}")
    
    def load_models(self, model_dir='../../models/'):
        """Load pre-trained models."""
        self.model_regression = joblib.load(model_dir + 'campaign_regression_model.pkl')
        self.model_classification = joblib.load(model_dir + 'campaign_classification_model.pkl')
        self.scaler = joblib.load(model_dir + 'campaign_scaler.pkl')
        self.feature_columns = joblib.load(model_dir + 'campaign_features.pkl')
        
        print("✅ Models loaded successfully")


if __name__ == "__main__":
    # Example usage
    print("\n" + "="*80)
    print("CAMPAIGN ROI & REDEMPTION PREDICTOR")
    print("="*80)
    
    # Initialize predictor
    predictor = CampaignRedemptionPredictor()
    
    # Load and prepare data
    data = predictor.load_and_prepare_data()
    data = predictor.engineer_features()
    
    # Prepare training data
    X_train, X_test, y_train, y_test, X_train_orig, X_test_orig = predictor.prepare_training_data()
    
    # Train models
    reg_results = predictor.train_regression_models(X_train, X_test, y_train, y_test)
    clf_results = predictor.train_classification_models(X_train, X_test, y_train, y_test)
    
    # Feature importance
    importance = predictor.analyze_feature_importance(X_train_orig)
    
    # Save models
    predictor.save_models()
    
    print("\n" + "="*80)
    print("TRAINING COMPLETE!")
    print("="*80)
