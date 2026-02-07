import plotly.express as px
from business_trends_content import business_trends_sections
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import date
# API Configuration
API_BASE = "http://localhost:5000"

def fetch_data(endpoint, params=None):
    try:
        response = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=60)
        if response.status_code == 200:
            return response.json() # Return the whole dictionary immediately
        return None
    except Exception as e:
        st.error(f"Connection Error: {e}") # Show the actual error in the UI
        return None

def safe_columns(df, required_cols):
    available_cols = [col for col in required_cols if col in df.columns]
    return df[available_cols] if available_cols else df

# Page configuration
st.set_page_config(
    page_title="Fresh Flow Markets",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# Initialize session state for page routing if it doesn't exist
if 'page' not in st.session_state:
    st.session_state.page = "Main Statistics"

# Create clickable text links using columns


_, nav_col_home, nav_col_trends, nav_col1, nav_col2, nav_col3, logo_col = st.columns([1, 2, 2, 2, 2, 2, 2])

with nav_col_home:
    if st.button("Home"):
        st.session_state.page = "Home"
        st.rerun()
with nav_col_trends:
    if st.button("Business Trends"):
        st.session_state.page = "Business Trends"
        st.rerun()
with nav_col1:
    if st.button("Main Statistics"):
        st.session_state.page = "Main Statistics"
        st.rerun()
with nav_col2:
    if st.button("Inventory Management"):
        st.session_state.page = "Inventory Management"
        st.rerun()
with nav_col3:
    if st.button("Forecasting Suggestions"):
        st.session_state.page = "Forecasting Suggestions"
        st.rerun()
with logo_col:
    st.image("logo.png.jpeg", width=80)

# Update the 'page' variable used for routing in the rest of your script
page = st.session_state.page

st.markdown("---")

# --- CONDITIONAL SIDEBAR ---
# Features only appear when Inventory Management is selected
if page == "Inventory Management":
    with st.sidebar:
        st.title("Fresh Flow Markets")
        st.markdown("---")
        st.header("⚙️ Filters")
        per_page = st.selectbox("Items per page", [10, 20, 50], index=1)
        search_term = st.text_input("🔍 Search Items", placeholder="Enter item name or barcode")
        page_num = st.number_input("Page", min_value=1, value=1)
        st.markdown("---")
        st.caption("Deloitte x AUC Hackathon")
else:
    # This hides the sidebar on other pages by forcing it collapsed 
    # or simply leaving it empty as per Streamlit's behavior.
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def show_dashboard():
    """Main Statistics Dashboard"""
    st.title("📊 Fresh Flow Markets - Sales Dashboard")
    
    col_date1, col_date2 = st.columns([2, 1])
    with col_date1:
        days = st.selectbox(
            "📅 Select Time Period",
            options=[30, 90, 180, 365, 730, 1095, 1825],
            index=5,
            format_func=lambda x: f"Last {x} days ({x//365} years)" if x >= 365 else f"Last {x} days"
        )
    with col_date2:
        st.metric("Data Range", f"{days} days")

    with st.spinner("Fetching latest data..."):
        analytics = fetch_data("/api/analytics/dashboard", params={"days": days})
        orders_meta = fetch_data("/api/orders", params={"per_page": 1})

    total_orders = 0
    total_revenue = 0.0
    aov = 0.0
    
    if orders_meta and orders_meta.get('success'):
        total_orders = orders_meta.get('pagination', {}).get('total', 399810)
    elif analytics and 'data' in analytics and 'summary' in analytics['data']:
        total_orders = analytics['data']['summary'].get('total_orders', 0)
    
    if analytics and 'data' in analytics and 'summary' in analytics['data']:
        summary = analytics['data']['summary']
        total_revenue = float(summary.get('total_revenue') or 0.0)
        aov = float(summary.get('avg_order_value') or 0.0)
    
    if total_revenue > 0 and total_orders > 0:
        aov = total_revenue / total_orders

    st.subheader("🎯 Key Business Metrics")
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Total Transactions", f"{total_orders:,}")
    with m2: 
        rev_str = f"${total_revenue:,.2f}" if total_revenue < 1000000 else f"${total_revenue/1000000:.2f}M"
        st.metric("Total Revenue", rev_str)
    with m3: st.metric("Average Order Value", f"${aov:.2f}")

    st.divider()

    st.subheader("📦 Order Counts by Status")
    status_data = []
    if analytics and 'data' in analytics:
        status_data = analytics['data'].get('by_status', [])
    
    if status_data and len(status_data) > 0:
        df_status = pd.DataFrame(status_data)
        cols = st.columns(min(4, len(df_status)))
        for idx, status_row in enumerate(df_status.itertuples()):
            with cols[idx % len(cols)]:
                count = status_row.count
                if status_row.status is None or pd.isna(status_row.status):
                    status_name = "Unknown"
                else:
                    status_name = str(status_row.status).replace('_', ' ').title()
                st.metric(status_name, f"{count:,}")
    else:
        st.info("📊 No order status data available for the selected period")
    
    st.divider()

    st.subheader("📊 Order Status Distribution")
    if status_data and len(status_data) > 0:
        df_status = pd.DataFrame(status_data)
        col_pie, col_stat_table = st.columns([2, 1])
        with col_pie:
            fig_pie = px.pie(df_status, values='count', names='status', hole=0.4)
            st.plotly_chart(fig_pie, width="stretch")
        with col_stat_table:
            st.dataframe(df_status, width="stretch", hide_index=True)
    else:
        st.info("📊 No status distribution data available")

    st.divider()

    st.subheader("🏆 Top Selling Items")
    top_items_raw = analytics['data'].get('top_items', []) if analytics and 'data' in analytics else []

    if top_items_raw and len(top_items_raw) > 0:
        df_top = pd.DataFrame(top_items_raw)
        mapping = {'title': 'Item Name', 'order_count': 'Orders', 'total_quantity': 'Units Sold', 'revenue': 'Revenue'}
        df_top = df_top.rename(columns=mapping)
        item_col = 'Item Name'
        val_col = 'Orders'

        col_chart, col_table = st.columns([2, 1])
        with col_chart:
            fig = px.bar(df_top.head(5), x=val_col, y=item_col, orientation='h', color=val_col)
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, width="stretch")
        with col_table:
            st.dataframe(df_top, width="stretch", hide_index=True)
    else:
        st.info("📊 No top selling items data available")

    if st.button("🔄 Refresh Dashboard", type="primary"):
        st.rerun()

def show_inventory():
    """Inventory Management Page"""
    st.title("📦 Inventory Management")
    st.markdown("**Monitor and manage your inventory items**")
    
    with st.expander("ℹ️ How to Use the Inventory Dashboard", expanded=False): 
     st.markdown("""
    ### **Inventory Management Dashboard**
    
    This dashboard provides centralized control over your inventory. Use the tools below to maintain optimal stock levels, track item details, and ensure efficient operations.
    
    **Key Functionalities:**
    * **Search & Filter:** Locate specific items instantly using the search bar in the sidebar.
    * **Item Details:** View comprehensive information for each product by selecting it from the list.
    * **Low Stock Monitoring:** Items below their defined threshold are automatically highlighted for review.
    * **View Customization:** Adjust the number of items displayed per page using the selector in the sidebar.
    
    **Pro Tip:** Regularly check the "Low Stock" list to prevent inventory shortages.
    """)

    # Use variables from the conditional sidebar defined at top
    params = {
        'page': page_num,
        'per_page': per_page
    }
    if search_term:
        params['search'] = search_term
        params['page'] = 1

    data = fetch_data('/api/inventory/items', params)
    
    if data and data.get('data'):
        items = data['data']
        pagination = data.get('pagination', {})
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        df = pd.DataFrame(items)
        tab1, tab2, tab3 = st.tabs(["📋 All Items", "📊 Item Details", "🚨 Low Stock"])
        
        with tab1:
            st.subheader("All Inventory Items")
            display_cols = ['title', 'barcode', 'price', 'vat', 'status']
            available_cols = [col for col in display_cols if col in df.columns]
            
            if available_cols:
                display_df = df[available_cols].copy()
                if 'price' in display_df.columns:
                    display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
                if 'vat' in display_df.columns:
                    display_df['vat'] = display_df['vat'].apply(lambda x: f"{x}%" if pd.notna(x) else "N/A")
                st.dataframe(display_df, width="stretch", hide_index=True)
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
             st.info(f"📊 Showing {len(items)} items | Page {pagination.get('page', 1)} of {pagination.get('pages', 1)} | Total: {pagination.get('total', 0)}")
        
        
        with tab2:
            st.subheader("Item Details")
            if len(items) > 0:
                selected_item = st.selectbox(
                    "Select an item to view details:",
                    options=range(len(items)),
                    format_func=lambda i: items[i].get('title', f'Item {i+1}')
                )
                item = items[selected_item]
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Basic Info")
                    st.write(f"**ID:** {item.get('id', 'N/A')}")
                    st.write(f"**Title:** {item.get('title', 'N/A')}")
                    st.write(f"**Barcode:** {item.get('barcode', 'N/A')}")
                    st.write(f"**Price:** ${item.get('price', 0):.2f}")
                    st.write(f"**VAT:** {item.get('vat', 0)}%")
                    st.write(f"**Status:** {item.get('status', 'N/A')}")
                with col2:
                    st.markdown("### Availability")
                    st.write(f"**Display for Customers:** {'Yes' if item.get('display_for_customers') else 'No'}")
                    st.write(f"**Delivery:** {'Yes' if item.get('delivery') else 'No'}")
                    st.write(f"**Eat In:** {'Yes' if item.get('eat_in') else 'No'}")
                    st.write(f"**Takeaway:** {'Yes' if item.get('takeaway') else 'No'}")
        
       
        
        with tab3:
            st.subheader("🚨 Low Stock Alerts")
            low_stock_response = fetch_data('/api/inventory/low-stock')
            
            if low_stock_response and low_stock_response.get('data'):
                ls_df = pd.DataFrame(low_stock_response['data'])
                # Only show the ID and Name (Title) as requested
                cols = [c for c in ['title','id', 'current_stock'] if c in ls_df.columns]
                st.dataframe(ls_df[cols], width="stretch", hide_index=True)
            else:
                st.info("No low stock items found.")
    else:
        st.warning("⚠️ No inventory data available. Please check API connection.")

    
    if st.button("🔄 Refresh Inventory", type="primary"):
        st.rerun()

def show_forecasting():
    """Forecasting Suggestions Page"""
    st.title("🔮 Demand Forecasting & Reorder Suggestions")
    st.markdown("**AI-powered predictions to optimize your inventory**")
    
    ml_health = fetch_data('/api/ml/health')
    if ml_health and ml_health.get('status') == 'healthy':
        st.success("✅ ML Service is operational")
        with st.expander("📊 Available ML Models"):
            models = ml_health.get('available_models', {})
            for model_name, available in models.items():
                status = "✅ Ready" if available else "❌ Not Available"
                st.write(f"**{model_name.replace('_', ' ').title()}:** {status}")
    else:
        st.warning("⚠️ ML Service may not be fully operational")
    
    st.markdown("---")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Demand Forecast", 
        "📦 Reorder Recommendations", 
        "🔄 Bulk Forecast",
        "🎯 Campaign ROI",
        "👥 Customer Churn",
        "🏪 Cashier Integrity and Operational Risk"

    ])
    with tab1:
        st.subheader("Predict Item Demand")
        col1, col2 = st.columns([2, 1])
        with col1:
            item_id = st.number_input("Item ID", min_value=1, value=1, help="Enter the ID of the item to forecast")
            forecast_days = st.slider("Forecast Period (days)", min_value=1, max_value=30, value=7)
        with col2:
            is_holiday = st.checkbox("Is Holiday Period?", value=False)
            is_weekend = st.checkbox("Is Weekend?", value=False)
            campaign_active = st.checkbox("Campaign Active?", value=False)
        
        if st.button("🔮 Generate Forecast", type="primary"):
            with st.spinner("Generating forecast..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/api/ml/forecast/demand",
                        json={
                            "item_id": item_id,
                            "forecast_days": forecast_days,
                            "is_holiday": is_holiday,
                            "is_weekend": is_weekend,
                            "campaign_active": campaign_active
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            forecast_data = result['data']
                            if 'item_details' in forecast_data:
                                item_info = forecast_data['item_details']
                                st.success(f"**Forecast for:** {item_info.get('name', 'Unknown Item')}")
                                st.metric("Current Price", f"${item_info.get('current_price', 0):.2f}")
                            
                            # Show forecast status message if available
                            if 'message' in forecast_data:
                                st.info(f"ℹ️ {forecast_data['message']}")
                            
                            st.subheader("Forecast Results")
                            
                            # Calculate total demand from predictions array
                            if 'predictions' in forecast_data:
                                daily_df = pd.DataFrame(forecast_data['predictions'])
                                total_demand = daily_df['predicted_quantity'].sum()
                                avg_daily_demand = daily_df['predicted_quantity'].mean()
                                
                                cols = st.columns(2)
                                with cols[0]: st.metric("Total Predicted Demand", f"{total_demand:.1f} units")
                                with cols[1]: st.metric("Avg Daily Demand", f"{avg_daily_demand:.1f} units/day")
                                
                                fig = px.line(daily_df, x='date', y='predicted_quantity', title=f'{forecast_days}-Day Demand Forecast')
                                st.plotly_chart(fig, width="stretch")
                                st.dataframe(daily_df, width="stretch", hide_index=True)
                            else:
                                st.warning("No forecast predictions available in the response.")
                        else:
                            st.error(f"Error: {result.get('error', 'Unknown error')}")
                    else:
                        st.error(f"API Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Failed to generate forecast: {str(e)}")

    with tab2:
        st.subheader("Stock Reorder Recommendations")
        col1, col2 = st.columns(2)
        with col1:
            reorder_item_id = st.number_input("Item ID for Reorder", min_value=1, value=1, key="reorder_item")
            current_stock = st.number_input("Current Stock Level", min_value=0.0, value=100.0, step=1.0)
        with col2:
            lead_time = st.number_input("Lead Time (days)", min_value=1, value=3)
            safety_multiplier = st.slider("Safety Stock Multiplier", min_value=1.0, max_value=2.0, value=1.2, step=0.1)
        
        if st.button("📦 Get Reorder Recommendation", type="primary"):
            with st.spinner("Calculating..."):
                try:
                    response = requests.post(f"{API_BASE}/api/ml/forecast/reorder-recommendations", json={
                        "item_id": reorder_item_id, "current_stock": current_stock,
                        "lead_time_days": lead_time, "safety_stock_multiplier": safety_multiplier
                    }, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            reorder_data = result['data']
                            recommendations = reorder_data.get('recommendations', {})
                            
                            # Display key metrics
                            cols = st.columns(4)
                            with cols[0]: st.metric("Reorder Quantity", f"{recommendations.get('reorder_quantity', 0):.0f}")
                            with cols[1]: st.metric("Safety Stock", f"{recommendations.get('safety_stock_level', 0):.0f}")
                            with cols[2]: st.metric("Predicted Demand", f"{reorder_data.get('predicted_demand', 0):.0f}")
                            with cols[3]: st.metric("Urgency", recommendations.get('urgency', 'N/A').upper())
                            
                            # Additional info
                            if recommendations.get('reorder_needed'):
                                st.warning(f"⚠️ Reorder needed! Stockout expected: {recommendations.get('days_until_stockout', 'N/A')}")
                            else:
                                st.success("✅ Stock levels adequate")
                        else: st.error(f"Error: {result.get('error', 'Unknown error')}")
                except Exception as e: st.error(f"Failed: {str(e)}")

    with tab3:
        st.subheader("Bulk Item Forecast")
        item_ids_input = st.text_area("Item IDs (comma-separated)", value="1, 2, 3, 4, 5")
        bulk_forecast_days = st.slider("Forecast Days", min_value=1, max_value=30, value=7, key="bulk_days")
        if st.button("🔄 Generate Bulk Forecast", type="primary"):
            try:
                item_ids = [int(x.strip()) for x in item_ids_input.split(',') if x.strip()]
                response = requests.post(f"{API_BASE}/api/ml/forecast/bulk-items", json={"item_ids": item_ids, "forecast_days": bulk_forecast_days}, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        forecasts = result.get('forecasts', [])
                        summary_data = []
                        for f in forecasts:
                            # Calculate total demand from predictions array
                            predictions = f.get('predictions', [])
                            if predictions:
                                total_demand = sum(p.get('predicted_quantity', 0) for p in predictions)
                                avg_daily = total_demand / len(predictions) if predictions else 0
                                
                                # Make status more user-friendly
                                status = f.get('status', 'N/A')
                                if status == 'model_not_available':
                                    status_display = '⚠️ Fallback Estimate'
                                elif status == 'success':
                                    status_display = '✅ ML Prediction'
                                else:
                                    status_display = status
                                
                                summary_data.append({
                                    'Item ID': f.get('item_id'),
                                    'Total Demand': f"{total_demand:.1f}",
                                    'Avg Daily': f"{avg_daily:.1f}",
                                    'Status': status_display
                                })
                            else:
                                summary_data.append({
                                    'Item ID': f.get('item_id'),
                                    'Total Demand': '0.0',
                                    'Avg Daily': '0.0',
                                    'Status': '❌ No Data'
                                })
                        st.dataframe(pd.DataFrame(summary_data), width="stretch", hide_index=True)
            except Exception as e: st.error(f"Error: {str(e)}")
      #  TAB 4 FOR CAMPAIGN ROI ---
    with tab4:
        st.subheader("🎯 Campaign Success & ROI Predictor")
        st.markdown("Predict campaign performance before launch based on historical data.")
        
        c1, c2 = st.columns(2)
        with c1:
            # Inputs matching Campaign ROI Predictor requirements
            duration = st.number_input("Campaign Duration (Days)", min_value=1, value=7)
            points = st.number_input("Loyalty Points Awarded", min_value=0, value=200)
        with c2:
            discount = st.slider("Discount Percentage (%)", 0, 100, 20)
            min_spend = st.number_input("Minimum Spend Requirement ($)", min_value=0, value=75)
            
        if st.button("🚀 Predict ROI", type="primary"):
            with st.spinner("Analyzing campaign variables..."):
                try:
                    # Payload structure follows README.md quick start
                    roi_payload = {
                        "duration_days": duration,
                        "points": points,
                        "discount": discount,
                        "minimum_spend": min_spend
                    }
                    response = requests.post(f"{API_BASE}/api/ml/predict/campaigns", json=roi_payload, timeout=30)
                    
                    if response.status_code == 200:
                        res = response.json()
                        if res.get('success'):
                            data = res['data']
                            
                            # Reporting metrics as defined in ML_Models README
                            m_col1, m_col2 = st.columns(2)
                            with m_col1:
                                st.metric("Predicted Redemptions", f"{data.get('predicted_redemptions', 0)}")
                            with m_col2:
                                prob = data.get('success_probability_pct', 0)
                                st.metric("Success Probability", f"{prob}%")
                                
                            if prob > 80:
                                st.success("High probability of campaign success!")
                            else:
                                st.warning("Consider adjusting discount or minimum spend to improve ROI.")
                        else:
                            st.error(f"Prediction Error: {res.get('error')}")
                except Exception as e:
                    st.error(f"Could not connect to ROI model: {str(e)}")
    with tab5:
        st.subheader("Customer Churn and Loyalty Prediction")
        st.info("Predict individual customer churn risk and get retention recommendations.")

        with st.expander("🔍 Analyze Single Customer", expanded=True):
            with st.form("churn_form"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    cust_id = st.number_input("Customer ID", min_value=1, value=123)
                    waiting_time = st.number_input("Avg Waiting Time (min)", value=25.5)
                with col2:
                    rating = st.slider("Recent Rating (1-5)", 1.0, 5.0, 3.5)
                    points_c = st.number_input("Points Redeemed", value=500)
                with col3:
                    vip_thresh = st.number_input("VIP Threshold", value=1000)
                    last_order = st.number_input("Days Since Last Order", value=15)
                
                submit = st.form_submit_button("🔮 Predict Churn Risk", type="primary")

            if submit:
                with st.spinner("Analyzing customer behavior..."):
                    try:
                        payload = {
                            "customer_id": cust_id,
                            "recent_waiting_time": waiting_time,
                            "recent_rating": rating,
                            "points_redeemed": points_c,
                            "vip_threshold": vip_thresh,
                            "days_since_last_order": last_order
                        }
                        response = requests.post(f"{API_BASE}/api/ml/customers/churn-risk", json=payload, timeout=30)
                        
                        if response.status_code == 200:
                            res = response.json()
                            if res.get('success'):
                                data = res.get('data', {})
                                risk = data.get('churn_risk', {})
                                strat = data.get('retention_strategy', {})
                                insights = data.get('customer_insights', {})

                                st.success("Analysis Complete!")
                                m1, m2, m3 = st.columns(3)
                                prob_churn = risk.get('probability', 0)
                                m1.metric("Churn Probability", f"{prob_churn}%")
                                m2.metric("Risk Level", risk.get('level', 'N/A').upper())
                                m3.metric("Status", "VIP" if insights.get('is_vip') else "Standard")

                                st.write(f"**Risk Severity Assessment:** {risk.get('level', 'Unknown').title()}")
                                st.progress(prob_churn / 100)
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.markdown("#### 💡 Insights")
                                    st.write(f"- **Engagement:** {insights.get('engagement_level', 'N/A').title()}")
                                    st.write(f"- **Satisfaction:** {insights.get('satisfaction_score', 0)*100:.0f}%")
                                
                                with col_b:
                                    st.markdown("#### 🎯 Strategy")
                                    st.write(f"- **Urgency:** {strat.get('urgency', 'N/A').upper()}")
                                    for action in strat.get('recommended_actions', []):
                                        st.write(f"- {action}")
                    except Exception as e:
                        st.error(f"UI Transformation Failed: {str(e)}")

        st.markdown("---")
        st.subheader("📋 Batch Churn Risk Analysis")
        if st.button("Identify High-Risk Customers"):
            with st.spinner("Scanning customer base..."):
                try:
                    current_batch_payload = {
                        "customers": [{
                            "customer_id": cust_id,
                            "recent_waiting_time": waiting_time,
                            "recent_rating": rating,
                            "points_redeemed": points_c,
                            "vip_threshold": vip_thresh,
                            "days_since_last_order": last_order
                        }]
                    }
                    response = requests.post(f"{API_BASE}/api/ml/customers/batch-churn-risk", json=current_batch_payload, timeout=30)
                    
                    if response.status_code == 200:
                        batch_res = response.json()
                        if batch_res.get('success'):
                            bc1, bc2 = st.columns(2)
                            bc1.metric("Total Customers Scanned", batch_res.get('total_customers', 0))
                            bc2.metric("High Risk Count", batch_res.get('high_risk_count', 0), delta_color="inverse")
                            
                            if 'high_risk_customers' in batch_res:
                                table_data = []
                                for c in batch_res['high_risk_customers']:
                                    c_risk = c.get('churn_risk', {})
                                    table_data.append({
                                        "Customer ID": c.get('customer_id'),
                                        "Probability (%)": c_risk.get('probability'),
                                        "Risk Level": c_risk.get('level', 'N/A').upper()
                                    })
                                st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Batch prediction failed: {str(e)}") 


    
    st.markdown("---")
# Page routing
if page == "Home":
    # --- Redesigned Homepage Inspired by freshflow.ai ---
    st.markdown("""
        <div style='text-align:center;'>
            <img src='logo.png.jpeg' width='120'/>
        </div>
    """, unsafe_allow_html=True)
    st.title("Fuller Shelves, Less Waste")
    st.markdown("---")
    st.subheader("Empowering Retailers with AI-Driven Inventory Management")
    st.markdown("""
        Fresh Flow Markets leverages advanced AI to optimize inventory, reduce waste, and maximize profits for fresh produce departments. Our platform is designed to simplify ordering, forecasting, and supplier management for retailers of all sizes.
    """)
    st.markdown("---")
    st.markdown("### Why Choose Fresh Flow?")
    st.markdown("- Reduce stock-outs and waste\n- Boost revenue and margins\n- Make inventory management effortless\n- Empower your team with actionable insights\n- Seamless integration with your current systems")
    st.markdown("---")
    st.markdown("### What Our Customers Say")
    st.info("\"Fresh Flow Markets helped us decrease shrink and increase revenue. The outcome couldn't have been better!\"\n\n- Retail Store Owner")
    st.info("\"With Fresh Flow's AI, we reduced waste and improved customer satisfaction.\"\n\n- Grocery Manager")
    st.markdown("---")
    st.markdown("### Our Solution")
    st.markdown("- AI-powered demand forecasting\n- Intuitive inventory tracking\n- Easy supplier management\n- Effortless IT integration\n- Designed for fresh produce and retail environments")
    st.markdown("---")
    st.markdown("### Ready to try AI that really works for fresh produce?")
    st.markdown("[Book a Demo](https://calendly.com/mael-freshflow) | [Contact Us](mailto:support@freshflow.com)")
    st.caption("Deloitte x AUC Hackathon Project | v1.0.4-stable")
elif page == "Business Trends":
    st.title("📊 Business Trends")
    st.info("Explore key business trends, visualize patterns, and gain actionable insights from your data.")
    st.markdown("---")
    tabs = st.tabs([section['title'] for section in business_trends_sections])

    for idx, section in enumerate(business_trends_sections):
        with tabs[idx]:
            st.subheader(section['title'])
            st.markdown(section['description'])
            st.markdown("---")
            for img in section['images']:
                try:
                    st.image(img['file'], caption=img['caption'], use_column_width=True)
                    st.markdown(f"*{img.get('desc', '')}*")
                except Exception as e:
                    st.warning(f"Image not found or cannot be displayed: {img['file']} ({e})")
            st.markdown("---")
elif page == "Main Statistics":
    show_dashboard()
elif page == "Inventory Management":
    show_inventory()
elif page == "Forecasting Suggestions":
    show_forecasting()

    # --- UNIVERSAL FOOTER ---
st.markdown("---") # Visual separator
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("### 📞 Contact Us")
    st.caption("Fresh Flow Markets HQ")
    st.caption("Email: support@freshflow.com")
    st.caption("Phone: +1 (555) 012-3456")

with footer_col2:
    st.markdown("### 🛠️ Technical Support")
    st.caption("System Status: Online")
    st.caption("Documentation: [Click Here](#)")
    st.caption("Bug Report: [Open Ticket](#)")

with footer_col3:
    st.markdown("### 🏢 About")
    st.caption("Deloitte x AUC Hackathon Project")
    st.caption("© 2026 Fresh Flow Markets")
    st.caption("v1.0.4-stable")