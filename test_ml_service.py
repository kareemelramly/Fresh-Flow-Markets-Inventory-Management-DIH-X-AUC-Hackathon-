"""Test ML Prediction Service directly"""
import sys
sys.path.append('.')

from src.services.ml_prediction_service import MLPredictionService

print("="*80)
print("TESTING ML PREDICTION SERVICE")
print("="*80)

ml = MLPredictionService()

# Check models
print("\n1. Checking available models...")
available = ml.get_available_models()
for model_name, is_available in available.items():
    status = "✅ Available" if is_available else "❌ Not Available"
    print(f"   {model_name}: {status}")

# Health check
print("\n2. ML Service Health Check...")
health = ml.health_check()
print(f"   Status: {health['status']}")
print(f"   Ready Models: {health['ready_models']}/{health['total_models']}")
print(f"   Models Directory: {health['models_directory']}")

# Test campaign prediction with correct params
print("\n3. Testing Campaign Prediction...")
try:
    result = ml.predict_campaign_performance(
        duration_days=30,
        points=50,
        discount_percent=10,
        minimum_spend=100
    )
    print(f"   Status: {result.get('status', 'unknown')}")
    if 'predictions' in result:
        print(f"   ✅ Prediction successful!")
        print(f"   Expected redemptions: {result['predictions'].get('expected_redemptions', 'N/A')}")
    else:
        print(f"   Message: {result.get('message', 'N/A')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*80)
