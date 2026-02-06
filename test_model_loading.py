"""Test loading Campaign models directly"""
import joblib
import os

print("="*80)
print("TESTING MODEL LOADING")
print("="*80)

models_dir = 'models'
model_files = {
    'regressor': 'campaign_redemption_regressor.pkl',
    'classifier': 'campaign_success_classifier.pkl',
    'scaler': 'campaign_scaler.pkl',
    'features': 'campaign_features.pkl'
}

print(f"\nModels directory: {models_dir}")
print(f"Directory exists: {os.path.exists(models_dir)}")

for name, filename in model_files.items():
    filepath = os.path.join(models_dir, filename)
    print(f"\n{name.upper()}:")
    print(f"  Path: {filepath}")
    print(f"  Exists: {os.path.exists(filepath)}")
    
    try:
        model = joblib.load(filepath)
        print(f"  ✅ Loaded successfully")
        print(f"  Type: {type(model).__name__}")
    except Exception as e:
        print(f"  ❌ Failed to load: {e}")

print("\n" + "="*80)
