# 🎯 Campaign ROI & Redemption Predictor

**Fresh Flow Markets - Deloitte x AUC Hackathon**  
**Date:** February 5, 2026  
**Status:** ✅ Production Ready

---

## 🚀 Quick Start

### 1. Run the Notebook
Open and run [campaign_roi_predictor.ipynb](campaign_roi_predictor.ipynb) to see the full analysis and model training.

### 2. Use the API
```python
from campaign_predictor_api import predict_campaign

# Predict campaign success
result = predict_campaign(
    duration_days=7,      # 7-day campaign
    points=200,           # 200 loyalty points
    discount=20,          # 20% discount
    minimum_spend=75      # 75 DKK minimum
)

print(f"Expected Redemptions: {result['predicted_redemptions']}")
print(f"Success Probability: {result['success_probability_pct']}%")
print(f"ROI: {result['roi_percentage']}%")
print(f"Recommendation: {result['recommendation']}")
```

### 3. View Results
Check [CAMPAIGN_PREDICTOR_SUMMARY.md](CAMPAIGN_PREDICTOR_SUMMARY.md) for detailed performance metrics and insights.

---

## 📊 What This Model Does

**Before launching a campaign, it predicts:**
1. ✅ **How many times** it will be redeemed
2. ✅ **Probability of success** (launch or optimize)
3. ✅ **Expected ROI** and revenue impact

**Business Value:**
- Find the "sweet spot" for discounts
- Prevent failed campaigns (save money)
- Maximize ROI while protecting margins

---

## 🏆 Model Performance

| Model | Purpose | Metric | Score |
|-------|---------|--------|-------|
| **Gradient Boosting** | Predict redemption count | R² | **96.67%** |
| **Random Forest** | Predict success probability | AUC-ROC | **99.90%** |

**Accuracy:** The model predicts within **±0.42 redemptions** of actual results!

---

## 📁 Project Structure

```
├── campaign_roi_predictor.ipynb          # Main analysis notebook (START HERE)
├── CAMPAIGN_PREDICTOR_SUMMARY.md         # Detailed results & insights
├── campaign_predictor_api.py             # Production-ready API
├── src/models/campaign_redemption_predictor.py  # Training class
├── models/                               # Trained models
│   ├── campaign_redemption_regressor.pkl
│   ├── campaign_success_classifier.pkl
│   ├── campaign_scaler.pkl
│   └── campaign_features.pkl
└── data/Inventory Management/            # Source data
    ├── fct_campaigns.csv
    ├── fct_bonus_codes.csv
    └── ...
```

---

## 🎯 Hackathon Requirements ✅

| Requirement | Status | Details |
|------------|--------|---------|
| **Model Type:** Classification/Probability | ✅ | Random Forest Classifier (AUC: 99.90%) |
| **Goal:** Predict success probability | ✅ | 97.67% accuracy |
| **Goal:** Predict redemption count | ✅ | R²: 96.67% |
| **IV:** Duration of bonus code | ✅ | Feature importance: 11.7% |
| **IV:** Number of points | ✅ | Included in model |
| **IV:** Discount amount | ✅ | Key feature |
| **IV:** Offer details (min_spend) | ✅ | With interaction terms |
| **DV:** Redemptions frequency | ✅ | Primary target variable |
| **DV:** Redemptions per customer | ✅ | Available in analysis |
| **Business Value:** Find "sweet spot" | ✅ | Optimization function included |
| **Business Value:** Protect margins | ✅ | ROI calculation included |

---

## 💡 Key Insights

### What Makes Campaigns Successful?

1. **Max Redemptions Available** (50.8% importance)
   - More redemptions = higher success rate
   
2. **Campaign Duration** (11.7% importance)
   - Sweet spot: 3-7 days
   - Shorter campaigns = higher redemption rate per day
   
3. **Discount Sweet Spot**
   - 15-20% discount = optimal engagement
   - >30% discount = diminishing returns

4. **Timing Matters**
   - Launch month affects success
   - Hour of day impacts initial momentum

### Recommendations

✅ **DO:**
- Test campaigns with >70% predicted success
- Use 3-7 day duration for focused impact
- Set 15-20% discount for best ROI
- Require 50-100 DKK minimum spend

⚠️ **AVOID:**
- Over-discounting (>30%)
- Very long campaigns (>30 days)
- Zero minimum spend
- Launching without prediction

---

## 🔧 Technical Details

### Features Used (14 total)

**Primary (as specified):**
- `duration_days` - Campaign length
- `points` - Loyalty points offered
- `discount` - Discount percentage/amount
- `minimum_spend` - Order minimum requirement

**Supporting:**
- `redemptions` - Max redemptions available
- Campaign type indicators
- Temporal features (hour, day, month)
- Interaction terms

### Models Trained

1. **Regression Models:**
   - Linear Regression (baseline)
   - Random Forest Regressor
   - **Gradient Boosting** ⭐ (best: R² = 0.9667)

2. **Classification Models:**
   - Logistic Regression
   - **Random Forest Classifier** ⭐ (best: AUC = 0.9990)

### Dataset
- **641 campaigns** analyzed
- **512 training** / **129 test** split
- **20.44% success rate** overall
- **4.61 average redemptions** per campaign

---

## 📈 Example Predictions

### Scenario 1: Aggressive Campaign
```
Input:  Duration: 7 days | Points: 200 | Discount: 25% | Min: 50 DKK
Output: Redemptions: 22.0 | Success: 24% | ROI: 300% | → OPTIMIZE
```

### Scenario 2: Conservative Campaign
```
Input:  Duration: 3 days | Points: 100 | Discount: 10% | Min: 100 DKK
Output: Redemptions: 20.3 | Success: 22% | ROI: 900% | → OPTIMIZE
```

### Scenario 3: Optimal Settings
```
Input:  Duration: 7 days | Points: 200 | Discount: 15% | Min: 75 DKK
Output: Redemptions: 18.5 | Success: 78% | ROI: 450% | → LAUNCH
```

---

## 🎬 Demo in Notebook

Run [campaign_roi_predictor.ipynb](campaign_roi_predictor.ipynb) to see:
- ✅ Data exploration and visualization
- ✅ Feature engineering process
- ✅ Model training and comparison
- ✅ Feature importance analysis
- ✅ Interactive predictions
- ✅ Business insights and recommendations

---

## 📦 Installation & Requirements

All dependencies already installed:
- pandas, numpy
- scikit-learn
- matplotlib, seaborn
- joblib

---

## 🚀 Next Steps for Production

1. **Integration** - Connect to campaign management system
2. **Dashboard** - Build interactive UI for marketing team
3. **A/B Testing** - Validate predictions vs. actual results
4. **Continuous Learning** - Retrain monthly with new data
5. **API Deployment** - RESTful API for real-time predictions

---

## 📞 Contact & Support

For questions about the model or implementation:
- Review detailed summary: [CAMPAIGN_PREDICTOR_SUMMARY.md](CAMPAIGN_PREDICTOR_SUMMARY.md)
- Check API documentation: [campaign_predictor_api.py](campaign_predictor_api.py)
- Open the notebook: [campaign_roi_predictor.ipynb](campaign_roi_predictor.ipynb)

---

## 🏅 Project Status

**✅ COMPLETE & PRODUCTION READY**

- [x] Data analysis complete
- [x] Models trained (96.67% R² / 99.90% AUC)
- [x] API created and tested
- [x] Documentation complete
- [x] Hackathon requirements met
- [x] Ready for deployment

---

**Built with ❤️ for Fresh Flow Markets**  
*Deloitte x AUC Hackathon 2026*
