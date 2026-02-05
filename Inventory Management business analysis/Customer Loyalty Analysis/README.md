# Customer Loyalty Analysis - Fresh Flow Markets

## Overview

This folder contains a comprehensive customer loyalty analysis for Fresh Flow Markets, addressing the challenge of understanding and improving customer retention despite 99.24% of orders being anonymous guest checkouts.

## Contents

### Main Analysis
- **customer_loyalty_analysis.ipynb** - Complete Jupyter notebook with:
  - Data loading and preprocessing
  - RFM (Recency, Frequency, Monetary) segmentation
  - Customer lifetime value analysis
  - Campaign timing optimization
  - VIP vs Regular customer comparisons
  - Correlation analysis
  - Business insights and recommendations

### Exports (exports/)
Generated CSV files from the analysis:
- `customer_metrics.csv` - Individual customer metrics and segments
- `rfm_customer_segments.csv` - RFM segmentation results
- `segment_performance.csv` - Performance by customer segment
- `vip_vs_regular_comparison.csv` - VIP and regular customer comparison
- `campaign_timing_by_day.csv` - Best days for campaigns
- `campaign_timing_by_hour.csv` - Best hours for campaigns
- `correlation_matrix.csv` - Feature correlations
- `executive_summary.csv` - High-level summary statistics
- `business_insights.txt` - Detailed business recommendations

### Visualizations (visualizations/)
Charts and graphs generated during analysis:
- Orders by day of week
- Orders by hour of day
- Customer spending distribution
- RFM segment distribution
- Campaign timing heatmaps
- Correlation matrix heatmap

## Key Findings

### Critical Data Limitation
- **99.24% of orders** (396,756 out of 399,810) are anonymous guest checkouts
- Only **1,900 registered customers** with 2,486 trackable orders
- This severely limits traditional customer loyalty tracking

### Customer Segmentation (RFM Analysis)
Based on the 1,900 registered customers:
- **Champions**: High-value, recent, frequent customers
- **Loyal Customers**: Regular repeat purchasers
- **Potential Loyalists**: Recent customers with growth potential
- **At Risk**: Previously active customers showing decline
- **Lost**: Inactive customers needing re-engagement

### Recommendations
1. **Immediate**: Implement guest email/phone capture at checkout
2. **Short-term**: Incentivize account creation with loyalty points/discounts
3. **Long-term**: Enable retroactive order linking when guests register
4. **Alternative**: Use session-based analytics for guest behavior

## Technical Details

### Dependencies
- pandas
- numpy
- matplotlib
- seaborn
- scipy

### Data Source
- Original: `data/Uncleaned Inventory Management data/fct_orders.csv`
- Cleaned: `data/Inventory Management/fct_orders.csv`

### Data Cleaning Issues Fixed
The original data cleaning script had critical bugs:
- Incorrectly converted user_id field as Unix timestamp
- Removed 98.6% of registered customers through improper outlier detection
- **Fixed version** preserves 81.4% of customer data (1,900 customers vs. only 28)

## Usage

1. Open `customer_loyalty_analysis.ipynb` in Jupyter Notebook or VS Code
2. Ensure data files are in correct locations
3. Run cells sequentially from top to bottom
4. Exported files will be generated in the `exports/` folder
5. Visualizations can be found in the `visualizations/` folder

## Business Value

This analysis provides:
- Actionable customer segmentation for targeted marketing
- Optimal campaign timing to maximize engagement
- Clear understanding of VIP vs regular customer behavior
- Documented limitations and recommendations for platform improvements
- Foundation for implementing effective loyalty programs

## Authors

Created for the Deloitte x AUC Hackathon - Fresh Flow Markets Use Case

## Date

February 5, 2026
