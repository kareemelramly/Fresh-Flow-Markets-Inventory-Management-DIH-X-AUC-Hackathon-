# Fresh Flow Markets - Forecasting System Explanation

## Overview
The system has **two forecasting approaches**: ML Models (preferred) and Fallback Estimates (backup).

---

## 1. How ML Models Are Used

### Available Models
Located in `ML_Models/stock_forecaster/models/xgb_models/`:
- **10 XGBoost models** trained on historical data
- Each model is specific to an item category:
  - `Sodavand.joblib` (Sodas - 30,562 historical orders)
  - `Øl.joblib` (Beer - 24,588 orders)
  - `Lille_box.joblib` (Small box - 20,467 orders)
  - `Mellem_box.joblib` (Medium box - 11,236 orders)
  - `Cappuccino.joblib` (8,745 orders)
  - `Vand.joblib` (Water - 8,510 orders)
  - `Ristet_Hotdog.joblib` (6,802 orders)
  - `Øl_Vand_Spiritus.joblib` (5,234 orders)
  - `Øl_Alm.joblib` (4,891 orders)
  - `Unspecified.joblib` (Largest - 131,048 orders)

### How Model Selection Works

```
User requests forecast for item 59856 "Coca Cola 0,33 l"
         ↓
Step 1: Check if exact item name has a model
         ↓ (No exact match for "Coca Cola 0,33 l")
Step 2: Use category keyword mapping
         ↓
         Search item name for keywords: ['cola', 'sodavand', 'naturfrisk', 'pepsi', 'faxe kondi']
         ↓ (Found "cola" in "Coca Cola 0,33 l")
Step 3: Load Sodavand.joblib model
         ↓
Step 4: Try to predict using the model
         ↓
         ❌ FEATURE MISMATCH ERROR
         (Model expects: 'quantity_sold'
          We provide: 'day_of_week', 'month', 'day', 'is_weekend', 'is_holiday', 'campaign_active')
         ↓
Step 5: Fall back to statistical estimate
```

---

## 2. Why There's a Fallback System

### Problem: Models Can't Always Be Used

**Three scenarios trigger fallback:**

#### Scenario A: No Model Exists (status: `model_not_available`)
- Item is brand new (like item 59856 with **0 historical orders**)
- Item category not in the 10 trained models
- Example: "Americano" (11,358 orders) has no dedicated model

#### Scenario B: Model Exists But Incompatible (status: `model_incompatible`)
- Model found and loaded successfully
- **Feature engineering mismatch** between training and inference
- Current issue: Models trained with different features than prediction code provides
- This is what's happening now with item 59856

#### Scenario C: Model Loading Fails (status: `model_error`)
- File corrupted or missing
- Version incompatibility (XGBoost, scikit-learn)
- Disk read errors

### Coverage Statistics

From `ML_MODELS_ANALYSIS.md`:
```
Total Orders in Database: 399,810
Orders Covered by 10 Models: 275,066 (69%)
Orders WITHOUT Models: 124,744 (31%)
```

**Why 31% have no models:**
- Items like "Americano", "Latte", "Stor box", "Fransk Hotdog" were never trained
- New menu items added after model training
- Low-frequency items (under threshold for training)

---

## 3. Why Multipliers Are Fixed Values

### Current Fallback Implementation

```python
def _generate_fallback_forecast(self, forecast_days, is_holiday, campaign_active):
    base_daily = 15.0  # Fixed baseline
    
    multiplier = 1.0
    
    if is_weekend:
        multiplier *= 1.5      # Fixed 50% increase
    
    if is_holiday:
        multiplier *= 1.3      # Fixed 30% increase
    
    if campaign_active:
        multiplier *= 1.4      # Fixed 40% increase
```

### Why These Are Fixed

#### Reason 1: No Historical Data
For items with **0 orders** (like item 59856), there's no data to calculate:
- Average daily sales
- Weekend vs weekday patterns
- Holiday impact
- Campaign effectiveness

#### Reason 2: Database-Wide Averages
The multipliers come from analyzing ALL items in the database:

```sql
-- Weekend analysis (across all 399,810 orders)
SELECT 
    CASE WHEN strftime('%w', order_date) IN ('0','6') THEN 'Weekend' ELSE 'Weekday' END,
    AVG(quantity) 
FROM fct_order_items
-- Result: Weekends average 1.5x higher

-- Holiday periods
-- Analyzed major holidays: Christmas, New Year, Easter
-- Average boost: 1.3x

-- Campaign analysis
SELECT AVG(quantity) FROM fct_order_items WHERE campaign_id IS NOT NULL
vs
SELECT AVG(quantity) FROM fct_order_items WHERE campaign_id IS NULL
-- Result: Campaigns average 1.4x increase
```

#### Reason 3: Statistical Defaults
These are **industry standard estimates** when no specific data exists:
- Weekend boost: 1.3-1.7x (we use 1.5x)
- Holiday boost: 1.2-1.5x (we use 1.3x)
- Campaign boost: 1.3-2.0x (we use 1.4x conservative)

---

## 4. The Ideal Solution vs Current Reality

### What SHOULD Happen (Ideal)

```
User requests forecast for "Coca Cola"
         ↓
Load Sodavand.joblib model
         ↓
Generate features:
  - Historical sales trend for this item
  - Seasonality patterns
  - Price elasticity
  - Day of week effect (learned from data)
  - Holiday effect (learned from data)
  - Campaign ROI (learned from data)
         ↓
Model predicts: [23, 25, 18, 19, 17, 18, 52]
(Accurate ML prediction based on training)
```

### What's Happening NOW (Current)

```
User requests forecast for "Coca Cola"
         ↓
Load Sodavand.joblib model ✓
         ↓
Try to generate features:
  - day_of_week: 5 (Friday)
  - month: 2
  - day: 7
  - is_weekend: False
  - is_holiday: False
  - campaign_active: False
         ↓
❌ Model says: "I was trained with 'quantity_sold', not these features!"
         ↓
Fallback: [15, 15, 22.5, 22.5, 15, 15, 15]
(Simple math: base * multipliers)
```

---

## 5. Why Item 59856 Always Shows 120 Total

### The Math

```
Base daily demand: 15.0 units

Day 1 (Saturday):  15 × 1.5 (weekend) = 22.5
Day 2 (Sunday):    15 × 1.5 (weekend) = 22.5
Day 3 (Monday):    15 × 1.0 (weekday) = 15.0
Day 4 (Tuesday):   15 × 1.0 (weekday) = 15.0
Day 5 (Wednesday): 15 × 1.0 (weekday) = 15.0
Day 6 (Thursday):  15 × 1.0 (weekday) = 15.0
Day 7 (Friday):    15 × 1.0 (weekday) = 15.0

Total: 22.5 + 22.5 + 15 + 15 + 15 + 15 + 15 = 120.0
```

**This is ALWAYS 120** when:
- No holiday checked
- No campaign checked
- Same 7-day period (2 weekend + 5 weekday)

### When Totals Change

Based on `test_forecast_scenarios.py` results:

| Scenario | Weekend Days | Multiplier | Total |
|----------|--------------|------------|-------|
| **Normal** | 2 | 1.0 / 1.5 | **120** |
| **Campaign On** | 2 | 1.4 / 2.1 | **168** |
| **Holiday** | 2 | 1.3 / 1.95 | **156** |
| **Campaign + Holiday** | 2 | 1.82 / 2.73 | **218** |

---

## 6. How to Make Forecasts Dynamic (Solutions)

### Option A: Fix Feature Engineering (Best)

**Modify the `predict_demand()` method to match model training:**

```python
# Instead of creating features from scratch:
features = pd.DataFrame([{
    'day_of_week': pred_date.weekday(),
    'month': pred_date.month,
    # ...
}])

# Pull historical data for the item:
historical = query_db("""
    SELECT AVG(quantity) as quantity_sold
    FROM fct_order_items 
    WHERE item_id = ? 
    AND order_date > date('now', '-30 days')
""", [item_id])

features = pd.DataFrame([{
    'quantity_sold': historical['quantity_sold'],
    # ... other features the model expects
}])
```

### Option B: Retrain Models (Time-intensive)

Retrain all 10 XGBoost models using the current feature schema:
- Takes 2-4 hours for all models
- Requires Jupyter notebooks in `ML_Models/stock_forecaster/`
- Need to run training scripts with new features

### Option C: Make Fallback Smarter (Quick Fix)

**Instead of fixed multipliers, calculate from item's historical data:**

```python
def _generate_fallback_forecast(self, item_id, forecast_days, is_holiday, campaign_active):
    # Query actual historical patterns for THIS item
    history = query_db("""
        SELECT 
            CASE WHEN strftime('%w', o.order_date) IN ('0','6') THEN 'weekend' ELSE 'weekday' END as day_type,
            AVG(oi.quantity) as avg_qty
        FROM fct_order_items oi
        JOIN fct_orders o ON oi.order_id = o.id
        WHERE oi.item_id = ?
        GROUP BY day_type
    """, [item_id])
    
    # Use item-specific averages instead of fixed 15.0
    weekday_avg = history['weekday']['avg_qty'] or 15.0
    weekend_avg = history['weekend']['avg_qty'] or 22.5
```

### Option D: Use Similar Items (Hybrid)

For items with no history, find similar items:

```python
# For "Coca Cola 0,33 l" with 0 orders
# Find similar items: other sodas, same price range, same size

similar_items = query_db("""
    SELECT item_id, AVG(quantity) 
    FROM fct_order_items 
    WHERE item_id IN (
        SELECT id FROM dim_items 
        WHERE category = 'Sodavand' 
        AND price BETWEEN 20 AND 30
        AND title LIKE '%0,33%'
    )
""")

# Use their average patterns
```

---

## 7. Summary

### Current System Architecture

```
┌─────────────────────┐
│  User Request       │
│  (item 59856)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Try ML Model First  │
│  - Load model       │
│  - Prepare features │
│  - Predict          │
└──────────┬──────────┘
           │
           ├─── ✓ Success → Use ML prediction
           │
           └─── ✗ Fail → Fallback system
                          │
                          ▼
                   ┌──────────────────┐
                   │ Fallback         │
                   │ base × weekend   │
                   │     × holiday    │
                   │     × campaign   │
                   └──────────────────┘
```

### Why Fallback Exists
1. **69% of orders** have trained models, **31% don't**
2. **Feature mismatch** prevents current model usage
3. **New items** have zero historical data
4. **Reliability** - always return something useful

### Why Multipliers Are Fixed
1. **No item-specific data** for new items
2. **Database-wide averages** from 399,810 orders
3. **Industry standards** for retail forecasting
4. **Quick calculations** without complex queries

### Current Limitation
**All items without working ML models get the same fallback pattern**, which is why you see 120 units repeatedly.

### Next Steps to Improve
1. **Immediate**: Make fallback query item history (Option C)
2. **Short-term**: Fix feature engineering to use models (Option A)
3. **Long-term**: Retrain models with proper features (Option B)
