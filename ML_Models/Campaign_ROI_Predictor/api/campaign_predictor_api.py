"""
Campaign ROI & Redemption Predictor - Quick Start Guide
========================================================

This guide shows how to use the trained models to predict campaign success.
"""

import joblib
import pandas as pd
import numpy as np

# ============================================================================
# 1. LOAD TRAINED MODELS
# ============================================================================

def load_campaign_models():
    """Load all trained models and components."""
    models = {
        'regressor': joblib.load('models/campaign_redemption_regressor.pkl'),
        'classifier': joblib.load('models/campaign_success_classifier.pkl'),
        'scaler': joblib.load('models/campaign_scaler.pkl'),
        'features': joblib.load('models/campaign_features.pkl')
    }
    return models


# ============================================================================
# 2. PREDICT CAMPAIGN SUCCESS
# ============================================================================

def predict_campaign(duration_days, points, discount, minimum_spend,
                    max_redemptions=100, campaign_type='total_bill',
                    start_hour=12, start_day=0, start_month=1):
    """
    Predict campaign redemptions and success probability.
    
    Parameters:
    -----------
    duration_days : float
        Campaign duration in days (e.g., 7)
    points : int
        Loyalty points offered (e.g., 200)
    discount : float
        Discount percentage or amount (e.g., 20 for 20% off)
    minimum_spend : float
        Minimum purchase requirement in DKK (e.g., 50)
    max_redemptions : int, optional
        Maximum redemptions allowed (default: 100)
    campaign_type : str, optional
        'total_bill', 'specific_items', or 'freebie' (default: 'total_bill')
    start_hour : int, optional
        Hour of day 0-23 (default: 12)
    start_day : int, optional
        Day of week 0=Monday, 6=Sunday (default: 0)
    start_month : int, optional
        Month 1-12 (default: 1)
    
    Returns:
    --------
    dict
        - predicted_redemptions: Expected number of redemptions
        - success_probability: Probability of success (0-1)
        - recommendation: 'LAUNCH ✅' or 'OPTIMIZE ⚠️'
        - expected_revenue: Estimated revenue
        - roi_percentage: Expected ROI
    
    Example:
    --------
    >>> result = predict_campaign(
    ...     duration_days=7,
    ...     points=200,
    ...     discount=20,
    ...     minimum_spend=75
    ... )
    >>> print(f"Expected redemptions: {result['predicted_redemptions']}")
    >>> print(f"Success probability: {result['success_probability']*100:.1f}%")
    """
    
    # Load models
    models = load_campaign_models()
    
    # Prepare features
    is_percentage = 1
    is_total_bill = 1 if campaign_type == 'total_bill' else 0
    is_freebie = 1 if campaign_type == 'freebie' else 0
    is_weekend = 1 if start_day >= 5 else 0
    discount_per_min = discount / minimum_spend if minimum_spend > 0 else 0
    redemptions_per_dur = max_redemptions / duration_days if duration_days > 0 else 0
    
    input_data = pd.DataFrame([{
        'duration_days': duration_days,
        'points': points,
        'discount': discount,
        'minimum_spend': minimum_spend,
        'redemptions': max_redemptions,
        'is_percentage_discount': is_percentage,
        'is_total_bill_discount': is_total_bill,
        'is_freebie': is_freebie,
        'start_hour': start_hour,
        'start_day_of_week': start_day,
        'start_month': start_month,
        'is_weekend': is_weekend,
        'discount_per_min_spend': discount_per_min,
        'redemptions_per_duration': redemptions_per_dur
    }])
    
    # Ensure correct feature order
    input_data = input_data[models['features']]
    
    # Scale features
    input_scaled = models['scaler'].transform(input_data)
    
    # Predict
    predicted_redemptions = max(0, models['regressor'].predict(input_scaled)[0])
    success_probability = models['classifier'].predict_proba(input_scaled)[0, 1]
    
    # Calculate business metrics
    avg_order_value = minimum_spend if minimum_spend > 0 else 100
    expected_revenue = predicted_redemptions * avg_order_value
    
    if discount < 100:  # Percentage discount
        discount_cost = predicted_redemptions * (avg_order_value * discount / 100)
    else:  # Fixed amount
        discount_cost = predicted_redemptions * discount
    
    net_revenue = expected_revenue - discount_cost
    roi = (net_revenue / discount_cost * 100) if discount_cost > 0 else 0
    
    return {
        'predicted_redemptions': round(predicted_redemptions, 1),
        'success_probability': round(success_probability, 4),
        'success_probability_pct': round(success_probability * 100, 2),
        'expected_revenue': round(expected_revenue, 2),
        'discount_cost': round(discount_cost, 2),
        'net_revenue': round(net_revenue, 2),
        'roi_percentage': round(roi, 2),
        'recommendation': 'LAUNCH' if success_probability > 0.5 and predicted_redemptions > 5 else 'OPTIMIZE'
    }


# ============================================================================
# 3. BATCH PREDICTIONS
# ============================================================================

def predict_multiple_campaigns(campaigns_df):
    """
    Predict outcomes for multiple campaigns at once.
    
    Parameters:
    -----------
    campaigns_df : pandas.DataFrame
        DataFrame with columns: duration_days, points, discount, minimum_spend
    
    Returns:
    --------
    pandas.DataFrame
        Input DataFrame with added prediction columns
    
    Example:
    --------
    >>> campaigns = pd.DataFrame([
    ...     {'duration_days': 7, 'points': 200, 'discount': 20, 'minimum_spend': 75},
    ...     {'duration_days': 3, 'points': 100, 'discount': 15, 'minimum_spend': 50}
    ... ])
    >>> results = predict_multiple_campaigns(campaigns)
    """
    
    results = []
    for idx, row in campaigns_df.iterrows():
        prediction = predict_campaign(
            duration_days=row['duration_days'],
            points=row.get('points', 150),
            discount=row['discount'],
            minimum_spend=row['minimum_spend'],
            max_redemptions=row.get('max_redemptions', 100)
        )
        results.append(prediction)
    
    predictions_df = pd.DataFrame(results)
    return pd.concat([campaigns_df.reset_index(drop=True), predictions_df], axis=1)


# ============================================================================
# 4. OPTIMIZE CAMPAIGN PARAMETERS
# ============================================================================

def find_optimal_discount(duration_days, points, minimum_spend, 
                         target_redemptions=20, max_redemptions=100):
    """
    Find the optimal discount to achieve target redemptions.
    
    Parameters:
    -----------
    duration_days : float
        Campaign duration
    points : int
        Loyalty points
    minimum_spend : float
        Minimum purchase requirement
    target_redemptions : int
        Desired number of redemptions
    max_redemptions : int
        Maximum allowed redemptions
    
    Returns:
    --------
    dict
        - optimal_discount: Best discount percentage
        - predicted_redemptions: Expected redemptions at optimal discount
        - success_probability: Probability of success
    
    Example:
    --------
    >>> optimal = find_optimal_discount(
    ...     duration_days=7,
    ...     points=200,
    ...     minimum_spend=75,
    ...     target_redemptions=20
    ... )
    >>> print(f"Optimal discount: {optimal['optimal_discount']}%")
    """
    
    best_result = None
    best_diff = float('inf')
    
    # Test discounts from 5% to 50%
    for discount in range(5, 51, 5):
        result = predict_campaign(
            duration_days=duration_days,
            points=points,
            discount=discount,
            minimum_spend=minimum_spend,
            max_redemptions=max_redemptions
        )
        
        diff = abs(result['predicted_redemptions'] - target_redemptions)
        if diff < best_diff:
            best_diff = diff
            best_result = {
                'optimal_discount': discount,
                'predicted_redemptions': result['predicted_redemptions'],
                'success_probability': result['success_probability'],
                'roi_percentage': result['roi_percentage']
            }
    
    return best_result


# ============================================================================
# 5. USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    
    print("="*80)
    print("CAMPAIGN ROI & REDEMPTION PREDICTOR - EXAMPLES")
    print("="*80)
    
    # Example 1: Single prediction
    print("\n📊 Example 1: Predict Single Campaign")
    print("-" * 80)
    
    result = predict_campaign(
        duration_days=7,
        points=200,
        discount=20,
        minimum_spend=75,
        max_redemptions=150,
        campaign_type='total_bill'
    )
    
    print(f"\nCampaign Parameters:")
    print(f"  • Duration: 7 days")
    print(f"  • Points: 200")
    print(f"  • Discount: 20%")
    print(f"  • Min Spend: 75 DKK")
    print(f"\nPredictions:")
    print(f"  • Expected Redemptions: {result['predicted_redemptions']}")
    print(f"  • Success Probability: {result['success_probability_pct']}%")
    print(f"  • Expected Revenue: {result['expected_revenue']} DKK")
    print(f"  • ROI: {result['roi_percentage']}%")
    print(f"  • Recommendation: {result['recommendation']}")
    
    
    # Example 2: Find optimal discount
    print("\n\n📊 Example 2: Find Optimal Discount")
    print("-" * 80)
    
    optimal = find_optimal_discount(
        duration_days=7,
        points=200,
        minimum_spend=75,
        target_redemptions=25
    )
    
    print(f"\nTarget: 25 redemptions")
    print(f"  • Optimal Discount: {optimal['optimal_discount']}%")
    print(f"  • Predicted Redemptions: {optimal['predicted_redemptions']}")
    print(f"  • Success Probability: {optimal['success_probability']*100:.2f}%")
    print(f"  • Expected ROI: {optimal['roi_percentage']}%")
    
    
    # Example 3: Compare scenarios
    print("\n\n📊 Example 3: Compare Multiple Scenarios")
    print("-" * 80)
    
    scenarios = pd.DataFrame([
        {'name': 'Aggressive', 'duration_days': 7, 'points': 200, 'discount': 25, 'minimum_spend': 50, 'max_redemptions': 150},
        {'name': 'Moderate', 'duration_days': 7, 'points': 150, 'discount': 15, 'minimum_spend': 75, 'max_redemptions': 100},
        {'name': 'Conservative', 'duration_days': 3, 'points': 100, 'discount': 10, 'minimum_spend': 100, 'max_redemptions': 50},
    ])
    
    print("\nScenario Comparison:")
    for idx, row in scenarios.iterrows():
        result = predict_campaign(
            duration_days=row['duration_days'],
            points=row['points'],
            discount=row['discount'],
            minimum_spend=row['minimum_spend'],
            max_redemptions=row['max_redemptions']
        )
        print(f"\n{row['name']}:")
        print(f"  Redemptions: {result['predicted_redemptions']:.1f}")
        print(f"  Success: {result['success_probability_pct']}%")
        print(f"  ROI: {result['roi_percentage']:.1f}%")
        print(f"  {result['recommendation']}")
    
    
    print("\n" + "="*80)
    print("✅ Examples complete!")
    print("="*80)
