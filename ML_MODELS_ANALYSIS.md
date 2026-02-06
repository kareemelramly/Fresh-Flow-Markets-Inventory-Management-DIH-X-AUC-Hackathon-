# ML Models Analysis - Fresh Flow Markets

## Current Status

### ✅ Models Being Used (10 total)

| Model Name | Orders | Status | Location |
|------------|--------|--------|----------|
| **Unspecified** | 131,684 | ✅ Active | `ML_Models/stock_forecaster/models/xgb_models/Unspecified.joblib` |
| **Sodavand** | 30,259 | ✅ Active | `ML_Models/stock_forecaster/models/xgb_models/Sodavand.joblib` |
| **Øl** | 24,117 | ✅ Active | `ML_Models/stock_forecaster/models/xgb_models/Øl.joblib` |
| **Lille_box** | 19,855 | ✅ Active | `ML_Models/stock_forecaster/models/xgb_models/Lille_box.joblib` |
| **Mellem_box** | 17,267 | ✅ Active | `ML_Models/stock_forecaster/models/xgb_models/Mellem_box.joblib` |
| **Cappuccino** | 12,361 | ✅ Active | `ML_Models/stock_forecaster/models/xgb_models/Cappuccino.joblib` |
| **Vand** | 10,244 | ✅ Active | `ML_Models/stock_forecaster/models/xgb_models/Vand.joblib` |
| **Ristet_Hotdog** | 9,913 | ✅ Active | `ML_Models/stock_forecaster/models/xgb_models/Ristet_Hotdog.joblib` |
| **Øl_Vand_Spiritus** | 9,559 | ✅ Active | `ML_Models/stock_forecaster/models/xgb_models/Øl_Vand_Spiritus.joblib` |
| **Øl_Alm.** | 8,983 | ✅ Active | `ML_Models/stock_forecaster/models/xgb_models/Øl_Alm..joblib` |

**Total Coverage:** ~275,000 orders (matching these exact item names)

---

## ❌ Missing Models - High Priority Items

These high-volume items need ML models:

| Item Name | Order Count | Status | Priority |
|-----------|-------------|--------|----------|
| **Americano** | 11,680 | ⚠️ No Model | HIGH |
| **Stor box** | 9,784 | ⚠️ No Model | HIGH |
| **Fransk Hotdog** | 9,511 | ⚠️ No Model | HIGH |
| **Latte** | 9,307 | ⚠️ No Model | HIGH |
| **Alm Øl** | 7,744 | ⚠️ No Model | MEDIUM |
| **Pose / Poser** | 14,506 | ⚠️ No Model | HIGH |
| **Kildevand** | 6,699 | ⚠️ No Model | MEDIUM |
| **Alm Sandwich** | 6,536 | ⚠️ No Model | MEDIUM |
| **Kylling** | 6,166 | ⚠️ No Model | MEDIUM |
| **Brød** | 6,144 | ⚠️ No Model | MEDIUM |

**Total Missing:** ~87,000 orders without specific models

---

## 🔍 The Core Problem: Item Name Mismatch

### Why Item 59856 Shows "Fallback Estimate"

**Item 59856:** "Coca Cola 0,33 l"  
**Issue:** System looks for exact match `Coca Cola 0,33 l.joblib` which doesn't exist  
**Should Use:** `Sodavand.joblib` (the soda/soft drink category model)  
**Current Behavior:** Falls back to generic average (15-22.5 units/day)

### Other Examples:
- "Coca Cola Zero 0,33 l" → Should use **Sodavand** model
- "Naturfrisk Cola 0,25 l" → Should use **Sodavand** model  
- "Still Water 0,5 l" → Should use **Vand** model
- "Hot chocolate" → No suitable model exists

---

## 🛠️ Solutions

### Option 1: Add Category Mapping (QUICK FIX - Recommended)
Map specific item names to existing category models:

```python
ITEM_CATEGORY_MAPPING = {
    # Sodavand/Soft drinks
    'cola': 'Sodavand',
    'sodavand': 'Sodavand',
    'naturfrisk': 'Sodavand',
    'lemonade': 'Sodavand',
    
    # Water
    'water': 'Vand',
    'vand': 'Vand',
    'kildevand': 'Vand',
    
    # Beer
    'øl': 'Øl',
    'beer': 'Øl',
    'fadøl': 'Øl',
    
    # Coffee
    'cappuccino': 'Cappuccino',
    'latte': 'Cappuccino',  # Similar enough
    'americano': 'Cappuccino',  # Similar enough
    'kaffe': 'Cappuccino',
    
    # Boxes
    'lille box': 'Lille_box',
    'mellem box': 'Mellem_box',
    'stor box': 'Mellem_box',  # Use similar model
    
    # Hotdogs
    'hotdog': 'Ristet_Hotdog',
    'ristet': 'Ristet_Hotdog',
    'fransk': 'Ristet_Hotdog',
}
```

**Benefits:**
- ✅ Immediate improvement for ~70% of items
- ✅ No model retraining needed
- ✅ Better predictions than generic fallback

**Coverage Impact:**
- Before: 275K orders with ML models
- After: ~350K+ orders with ML models

---

### Option 2: Train New Models (LONG-TERM)
Train models for high-volume items without coverage:

**Priority 1 (>9K orders):**
1. Americano (11,680 orders)
2. Stor box (9,784 orders)
3. Fransk Hotdog (9,511 orders)
4. Latte (9,307 orders)

**Priority 2 (6-8K orders):**
5. Alm Øl (7,744)
6. Pose/Poser (14,506 combined)
7. Kildevand (6,699)
8. Alm Sandwich (6,536)
9. Kylling (6,166)
10. Brød (6,144)

**Estimated Impact:**
- Additional ~87,000 orders covered
- Total coverage: ~360K orders

---

## 📊 Current Model Utilization

### Models in ML_Models Directory:
1. ✅ **Campaign_ROI_Predictor** - ACTIVE (used in dashboard)
2. ✅ **stock_forecaster** - ACTIVE (10 item models)
3. ✅ **customer_churn** - AVAILABLE (model loaded)
4. ✅ **Operational_risk_predictors** - AVAILABLE (cashier risk)
5. ❌ **revenue_predictor** - NOT INTEGRATED

### Missing Integration:
- **revenue_predictor** model exists but not connected to API

---

## 💡 Recommendations

### Immediate Actions (This Week):
1. ✅ **Implement category mapping** for common items → Sodavand, Vand, Øl models
2. ✅ **Integrate revenue_predictor** model into API
3. ✅ **Add fuzzy matching** for item names (e.g., "Coca Cola" matches "Sodavand")

### Short-term (This Month):
4. 🔄 **Train 4 new models**: Americano, Latte, Stor box, Fransk Hotdog
5. 🔄 **Improve fallback logic** with historical sales data per item

### Long-term (Next Quarter):
6. 🔄 **Train models for top 30 items** (90% order coverage)
7. 🔄 **Auto-train models** for items with >1000 orders
8. 🔄 **Model refresh pipeline** (retrain monthly with new data)

---

## 🎯 Expected Results After Fixes

| Metric | Current | After Mapping | After New Models |
|--------|---------|---------------|------------------|
| Items with ML models | 10 items | ~50+ items | ~40 items |
| Order coverage | 275K (69%) | 350K (87%) | 360K (90%) |
| Prediction accuracy | Mixed | High | Very High |
| Fallback usage | 31% | 13% | 10% |

---

**Last Updated:** February 6, 2026  
**Analysis Date:** 2026-02-06  
**Total Items in Database:** 87,266  
**Total Orders:** ~400,000
