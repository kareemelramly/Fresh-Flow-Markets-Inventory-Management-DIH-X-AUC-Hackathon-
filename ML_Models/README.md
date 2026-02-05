# 🤖 Machine Learning Models

This folder contains production-ready machine learning models for Fresh Flow Markets.

---

## 📊 Available Models

### 1. Campaign ROI & Redemption Predictor ⭐

**Status:** ✅ Production Ready  
**Location:** [`Campaign_ROI_Predictor/`](./Campaign_ROI_Predictor/)

**What It Does:**
- Predicts campaign success before launch
- Forecasts redemption count with 96.67% accuracy  
- Calculates success probability with 99.90% AUC
- Optimizes discount levels for maximum ROI

**Performance:**
- Regression: R² = 96.67%, MAE = ±0.42 redemptions
- Classification: AUC = 99.90%, Accuracy = 97.67%

**Quick Start:**
```python
from Campaign_ROI_Predictor.api.campaign_predictor_api import predict_campaign

result = predict_campaign(
    duration_days=7,
    points=200,
    discount=20,
    minimum_spend=75
)

print(f"Expected Redemptions: {result['predicted_redemptions']}")
print(f"Success Probability: {result['success_probability_pct']}%")
```

**Resources:**
- 📖 [README](./Campaign_ROI_Predictor/README.md) - Quick start guide
- 📓 [Jupyter Notebook](./Campaign_ROI_Predictor/notebooks/campaign_roi_predictor.ipynb) - Training & analysis
- 🔧 [API Documentation](./Campaign_ROI_Predictor/api/campaign_predictor_api.py) - Production code
- 📊 [Full Report](./Campaign_ROI_Predictor/docs/CAMPAIGN_PREDICTOR_SUMMARY.md) - Analysis details

---

## 🚀 Future Models (Planned)

### 2. Inventory Demand Forecaster
**Status:** 🔜 Planned  
**Purpose:** Predict ingredient demand to optimize inventory levels

### 3. Customer Churn Predictor  
**Status:** 🔜 Planned  
**Purpose:** Identify at-risk customers for retention campaigns

### 4. Menu Item Success Predictor
**Status:** 🔜 Planned  
**Purpose:** Predict new menu item performance before launch

---

## 📁 Folder Structure

```
ML_Models/
├── README.md                           # This file
│
└── Campaign_ROI_Predictor/
    ├── README.md                       # Model quick start
    ├── notebooks/                      # Jupyter notebooks
    │   └── campaign_roi_predictor.ipynb
    ├── api/                            # Production code
    │   ├── campaign_predictor_api.py
    │   └── campaign_redemption_predictor.py
    ├── models/                         # Trained models
    │   ├── campaign_redemption_regressor.pkl
    │   ├── campaign_success_classifier.pkl
    │   ├── campaign_scaler.pkl
    │   └── campaign_features.pkl
    └── docs/                           # Documentation
        ├── CAMPAIGN_PREDICTOR_SUMMARY.md
        └── CAMPAIGN_TRAINING_COMPLETE.md
```

---

## 🎯 Model Selection Guide

| Business Need | Use This Model | Expected Outcome |
|---------------|----------------|------------------|
| Predict campaign success | Campaign ROI Predictor | Success probability + redemption count |
| Optimize discount level | Campaign ROI Predictor | Optimal discount % for target redemptions |
| Calculate campaign ROI | Campaign ROI Predictor | Expected revenue, cost, net profit |
| Forecast inventory needs | 🔜 Inventory Forecaster | Demand prediction by SKU |
| Prevent customer churn | 🔜 Churn Predictor | Risk score by customer |

---

## 📖 Documentation

- **[Main Project README](../README.md)** - Project overview
- **[Organization Summary](../ORGANIZATION_SUMMARY.md)** - Folder structure guide
- **[Database Schema](../database/DATABASE_SCHEMA.md)** - Data documentation

---

## 🏆 Model Performance Standards

All models in this folder meet these standards:
- ✅ **Accuracy:** >90% on test set
- ✅ **Documentation:** Complete notebooks + API docs
- ✅ **Testing:** Unit tests + integration tests
- ✅ **Deployment:** Production-ready code
- ✅ **Business Value:** Clear ROI demonstration

---

## 🛠️ Development

### Adding a New Model

1. Create folder: `ML_Models/Your_Model_Name/`
2. Follow the structure:
   ```
   Your_Model_Name/
   ├── README.md
   ├── notebooks/
   ├── api/
   ├── models/
   └── docs/
   ```
3. Include:
   - Training notebook with all cells executed
   - Production API code
   - Saved model files (.pkl)
   - Performance documentation
4. Update this README with the new model

### Requirements
```bash
pip install pandas numpy scikit-learn joblib matplotlib seaborn jupyter
```

---

**Last Updated:** February 5, 2026  
**Total Models:** 1 (Ready) + 3 (Planned)  
**Status:** ✅ Production Ready
