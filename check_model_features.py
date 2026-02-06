"""Check what features the Campaign model was trained with"""
import joblib

features = joblib.load('models/campaign_features.pkl')
print("="*80)
print("CAMPAIGN MODEL FEATURES")
print("="*80)
print(f"\nTotal features: {len(features)}")
print("\nFeature list:")
for i, feature in enumerate(features, 1):
    print(f"  {i:2d}. {feature}")
print("\n" + "="*80)
