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
                            st.error(f"❌ {result.get('error', 'Unknown error')}")
                    elif response.status_code == 400:
                        result = response.json()
                        st.error(f"❌ Cannot Generate Forecast")
                        st.warning(f"**Reason:** {result.get('error', 'Insufficient data')}")
                        if 'details' in result:
                            st.info(f"**Details:** Category: {result['details'].get('category_attempted', 'Unknown')}")
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
                        else:
                            st.error(f"❌ {result.get('error', 'Unknown error')}")
                    elif response.status_code == 400:
                        result = response.json()
                        st.error(f"❌ Cannot Calculate Reorder Recommendations")
                        st.warning(f"**Reason:** {result.get('error', 'Insufficient data')}")
                    else:
                        st.error(f"API Error: {response.status_code}")
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
                        errors_found = []
                        
                        for f in forecasts:
                            item_id = f.get('item_id')
                            
                            # Check if this forecast has an error
                            if f.get('status') == 'error':
                                errors_found.append(f"Item {item_id}: {f.get('error', 'Unknown error')}")
                                summary_data.append({
                                    'Item ID': item_id,
                                    'Total Demand': 'N/A',
                                    'Avg Daily': 'N/A',
                                    'Status': '❌ Error'
                                })
                            elif f.get('status') == 'success':
                                # Calculate total demand from predictions array
                                predictions = f.get('predictions', [])
                                if predictions:
                                    total_demand = sum(p.get('predicted_quantity', 0) for p in predictions)
                                    avg_daily = total_demand / len(predictions) if predictions else 0
                                    
                                    category = f.get('category_used', 'Unknown')
                                    summary_data.append({
                                        'Item ID': item_id,
                                        'Category': category,
                                        'Total Demand': f"{total_demand:.1f}",
                                        'Avg Daily': f"{avg_daily:.1f}",
                                        'Status': '✅ Success'
                                    })
                                else:
                                    summary_data.append({
                                        'Item ID': item_id,
                                        'Category': 'N/A',
                                        'Total Demand': 'N/A',
                                        'Avg Daily': 'N/A',
                                        'Status': '❌ No Data'
                                    })
                        
                        # Display results
                        if summary_data:
                            st.dataframe(pd.DataFrame(summary_data), width="stretch", hide_index=True)
                        
                        # Show errors if any
                        if errors_found:
                            st.error("⚠️ Some forecasts failed:")
                            for err in errors_found:
                                st.warning(err)
            except Exception as e: st.error(f"Error: {str(e)}")
     
    with tab4:
        # SECTION 1: SINGLE SCENARIO PREDICTOR
        st.subheader("🎯 1. Campaign ROI Predictor")
        st.markdown("Predict specific performance for a single campaign configuration.")
        
        with st.container():
            c1, c2 = st.columns(2)
            with c1:
                duration = st.number_input("Campaign Duration (Days)", min_value=1, value=7, key="dur_1")
                points = st.number_input("Loyalty Points Awarded", min_value=0, value=200, key="pts_1")
            with c2:
                discount = st.slider("Discount Percentage (%)", 0, 100, 20, key="disc_1")
                min_spend = st.number_input("Minimum Spend Requirement ($)", min_value=0, value=75, key="spend_1")
            
            if st.button("🚀 Predict ROI", type="primary", key="btn_1"):
                with st.spinner("Analyzing..."):
                    try:
                        roi_payload = {"duration_days": duration, "points": points, "discount_percent": discount, "minimum_spend": min_spend}
                        response = requests.post(f"{API_BASE}/api/ml/campaigns/predict", json=roi_payload, timeout=30)
                        if response.status_code == 200:
                            res = response.json()
                            if res.get('success'):
                                data = res['data']
                                preds = data.get('predictions', {})
                                rec = data.get('recommendation', {})
                                m_col1, m_col2, m_col3 = st.columns(3)
                                with m_col1: st.metric("Redemptions", f"{preds.get('expected_redemptions', 0):.0f}")
                                with m_col2: st.metric("Success Prob.", f"{preds.get('success_probability', 0):.1f}%")
                                with m_col3: st.metric("Action", rec.get('action', 'N/A').upper())
                                st.info(f"💡 **Reason:** {rec.get('reason', 'N/A')}")
                    except Exception as e: st.error(f"Error: {str(e)}")

        st.markdown("---")

        # SECTION 2: DISCOUNT OPTIMIZER
        st.subheader("💡 2. Discount Sensitivity Optimizer")
        st.markdown("Vary the discount levels to find the 'Sweet Spot' for your current strategy.")
        
        with st.container():
            oc1, oc2 = st.columns(2)
            with oc1:
                opt_dur = st.number_input("Fixed Duration (Days)", min_value=1, value=7, key="dur_2")
                opt_pts = st.number_input("Fixed Points", min_value=0, value=200, key="pts_2")
            with oc2:
                opt_spend = st.number_input("Fixed Min Spend ($)", min_value=0, value=75, key="spend_2")
            
            if st.button("🔍 Run Optimization Scan", key="btn_2"):
                with st.spinner("Simulating discount levels..."):
                    opt_results = []
                    # Testing range of discounts
                    for d_test in [5, 10, 15, 20, 25, 30, 40, 50, 75]:
                        try:
                            payload = {"duration_days": opt_dur, "points": opt_pts, "discount_percent": d_test, "minimum_spend": opt_spend}
                            r = requests.post(f"{API_BASE}/api/ml/campaigns/predict", json=payload, timeout=10)
                            if r.status_code == 200:
                                d = r.json().get('data', {}).get('predictions', {})
                                opt_results.append({"Discount %": d_test, "Redemptions": d.get('expected_redemptions', 0), "Prob (%)": d.get('success_probability', 0)})
                        except: continue
                    
                    if opt_results:
                        df_opt = pd.DataFrame(opt_results)
                        fig = px.line(df_opt, x="Discount %", y="Redemptions", markers=True, title="Expected Redemptions by Discount Level")
                        st.plotly_chart(fig, use_container_width=True)
                        best_d = df_opt.loc[df_opt['Redemptions'].idxmax()]
                        st.success(f"✅ **Optimal Discount:** {best_d['Discount %']}% yields the highest redemptions ({best_d['Redemptions']:.0f}).")

        st.markdown("---")

        # SECTION 3: BATCH SCENARIO COMPARISON
        st.subheader("📊 3. Batch Scenario Comparison")
        st.markdown("Compare a 'Conservative' (low reward) vs 'Aggressive' (high reward) strategy side-by-side.")
        
        with st.container():
            bc1, bc2 = st.columns(2)
            with bc1:
                base_dur = st.number_input("Base Duration", min_value=1, value=7, key="dur_3")
                base_pts = st.number_input("Base Points", min_value=0, value=200, key="pts_3")
            with bc2:
                base_disc = st.slider("Base Discount %", 0, 100, 20, key="disc_3")
                base_spend = st.number_input("Base Min Spend", min_value=0, value=75, key="spend_3")

            if st.button("📈 Compare Scenarios", key="btn_3"):
                with st.spinner("Processing batch comparison..."):
                    scenarios = [
                        {"Name": "Conservative", "d": base_dur, "p": int(base_pts*0.5), "disc": max(0, base_disc-10), "s": base_spend+25},
                        {"Name": "Current Base", "d": base_dur, "p": base_pts, "disc": base_disc, "s": base_spend},
                        {"Name": "Aggressive", "d": base_dur, "p": int(base_pts*1.5), "disc": min(100, base_disc+10), "s": max(0, base_spend-25)}
                    ]
                    comparison = []
                    for s in scenarios:
                        try:
                            payload = {"duration_days": s["d"], "points": s["p"], "discount_percent": s["disc"], "minimum_spend": s["s"]}
                            r = requests.post(f"{API_BASE}/api/ml/campaigns/predict", json=payload, timeout=10)
                            if r.status_code == 200:
                                d = r.json().get('data', {}).get('predictions', {})
                                comparison.append({"Scenario": s["Name"], "Redemptions": d.get('expected_redemptions', 0), "Prob (%)": d.get('success_probability', 0)})
                        except: continue
                    
                    if comparison:
                        df_comp = pd.DataFrame(comparison)
                        st.plotly_chart(px.bar(df_comp, x="Scenario", y="Redemptions", color="Prob (%)", text_auto='.0f', title="Strategic Comparison"), use_container_width=True)
                        st.dataframe(df_comp, hide_index=True, use_container_width=True)
    with tab5:
        st.subheader("Customer Churn and Loyalty Prediction")
        st.info("Predict individual customer churn risk and get retention recommendations.")

        with st.expander("🔍 Analyze Single Customer", expanded=True):
            with st.form("churn_form"):
                st.info("📊 Model uses 4 features: discount amount, points earned, average price, and waiting time")
                col1, col2 = st.columns(2)
                with col1:
                    cust_id = st.number_input("Customer ID", min_value=1, value=123)
                    discount_amount = st.number_input("Total Discount Amount ($)", min_value=0.0, value=25.0, step=10.0, help="Total discounts received")
                    points_earned = st.number_input("Points Earned", min_value=0.0, value=500.0, step=100.0)
                with col2:
                    price = st.number_input("Avg Order Price ($)", min_value=0.0, value=75.50, step=10.0)
                    waiting_time = st.number_input("Avg Waiting Time (min)", min_value=0.0, value=25.5, step=0.5)
                
                submit = st.form_submit_button("🔮 Predict Churn Risk", type="primary")

            if submit:
                with st.spinner("Analyzing customer behavior..."):
                    try:
                        payload = {
                            "customer_id": cust_id,
                            "discount_amount": discount_amount,
                            "points_earned": points_earned,
                            "price": price,
                            "waiting_time": waiting_time
                        }
                        response = requests.post(f"{API_BASE}/api/ml/customers/churn-risk", json=payload, timeout=30)
                        
                        if response.status_code == 200:
                            res = response.json()
                            if res.get('success'):
                                result = res.get('data', {})
                                # Check if model is ready
                                if result.get('status') == 'model_not_ready':
                                    st.warning(f"⚠️ {result.get('message', 'Model not available')}")
                                else:
                                    risk = result.get('churn_risk', {})
                                    strat = result.get('retention_strategy', {})
                                    insights = result.get('customer_insights', {})

                                    st.success("Analysis Complete!")
                                    m1, m2, m3 = st.columns(3)
                                    prob_churn = risk.get('probability', 0)
                                    m1.metric("Churn Probability", f"{prob_churn}%")
                                    m2.metric("Risk Level", risk.get('level', 'N/A').upper())
                                    m3.metric("Will Churn", "Yes" if risk.get('will_churn', False) else "No")

                                    st.write(f"**Risk Severity Assessment:** {risk.get('level', 'Unknown').title()}")
                                    st.progress(prob_churn / 100)
                                    
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.markdown("#### 💡 Customer Insights")
                                        st.write(f"- **Engagement:** {insights.get('engagement_level', 'N/A').title()}")
                                        st.write(f"- **Avg Order Value:** ${insights.get('avg_order_value', 0):.2f}")
                                        st.write(f"- **Discount Usage:** ${insights.get('discount_usage', 0):.2f}")
                                    
                                    with col_b:
                                        st.markdown("#### 🎯 Retention Strategy")
                                        st.write(f"**Urgency:** {strat.get('urgency', 'N/A').upper()}")
                                        st.write(f"**Estimated Cost:** ${strat.get('estimated_retention_cost', 0)}")
                                        st.markdown("**Recommended Actions:**")
                                        for action in strat.get('recommended_actions', []):
                                            st.write(f"- {action}")
                            else:
                                st.error(f"Error: {res.get('error', 'Unknown error')}")
                        else:
                            st.error(f"API Error: {response.status_code}")
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
                            "discount_amount": discount_amount,
                            "points_earned": points_earned,
                            "points_redeemed": points_redeemed,
                            "price": price,
                            "waiting_time": waiting_time,
                            "vip_threshold": vip_threshold,
                            "rating": rating
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

    with tab6:
        st.subheader("🏪 Cashier Integrity & Operational Risk Monitor")
        st.markdown("Detect anomalies in cashier performance using pre-calculated risk assessments.")
        
        # Quick Lookup from Pre-calculated Data
        st.markdown("### 🔍 Quick Risk Lookup")
        st.info("Enter Cashier ID to get pre-calculated risk assessment from historical analysis")
        
        with st.form("cashier_lookup_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                cashier_id_lookup = st.number_input("Cashier ID", min_value=1, value=22354, key="lookup_cashier", 
                                                   help="Try 22354 for a known high-risk example")
            with col2:
                st.write("")  # Spacing
                
            submit_lookup = st.form_submit_button("🔍 Get Risk Assessment", type="primary")
        
        if submit_lookup:
            with st.spinner(f"Looking up cashier {cashier_id_lookup}..."):
                try:
                    response = requests.get(f"{API_BASE}/api/ml/operations/cashier-risk-lookup/{cashier_id_lookup}", timeout=10)
                    
                    if response.status_code == 200:
                        res = response.json()
                        if res.get('success'):
                            result = res.get('data', {})
                            
                            st.success("✅ Cashier Found!")
                            
                            # Display risk info
                            col1, col2, col3, col4 = st.columns(4)
                            risk_prob = result.get('risk_probability', 0) * 100
                            col1.metric("Risk Probability", f"{risk_prob:.1f}%")
                            col2.metric("Risk Category", result.get('risk_category', 'N/A'))
                            col3.metric("Total Transactions", f"{result.get('num_transactions_sum', 0):,.0f}")
                            col4.metric("Amount of Transaction Total", f"${result.get('transaction_total_sum', 0):,.2f}")
                            
                            # Risk Level Indicator
                            if result.get('risk_category') == 'CRITICAL':
                                st.error(f"🚨 **CRITICAL RISK** - Immediate attention required!")
                            elif result.get('risk_category') == 'HIGH':
                                st.warning(f"⚠️ **HIGH RISK** - Review required")
                            elif result.get('risk_category') == 'MEDIUM':
                                st.info(f"🔵 **MEDIUM RISK** - Monitor closely")
                            else:
                                st.success("✅ **LOW RISK** - Normal operations")
                            
                            # Financial Details
                            st.markdown("#### 💰 Key Metrics")
                            f_col1, f_col2 = st.columns(2)
                            with f_col1:
                                st.metric("Max Discrepancy %", f"{result.get('balance_discrepancy_pct_max', 0):,.1f}%")
                                st.metric("Balance Difference", f"${result.get('balance_diff_sum', 0):,.2f}")
                            with f_col2:
                                st.metric("VAT Component", f"${result.get('vat_component_sum', 0):,.2f}")
                                st.metric("Anomaly Score", f"{result.get('anomaly_score', 0):.3f}")
                        else:
                            st.error(f"❌ {res.get('error', 'Unknown error')}")
                    elif response.status_code == 404:
                        st.warning(f"⚠️ Cashier {cashier_id_lookup} not found in pre-calculated assessments")
                        st.info("💡 Try the Manual Entry option below to analyze this cashier")
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        
        # Advanced Manual Entry (Collapsible)
        with st.expander("Advanced: Manual Feature Entry for new data", expanded=False):
            st.warning("Use this section **only if the cashier is not available in Quick Lookup**. "
        "Enter **summary statistics for one cashier during a single shift or time period**. "
        "If exact values are unknown, use **reasonable estimates**. "
        "Higher discrepancies, unusually large percentages, or high variability may indicate elevated risk." )
            
        
            col1, col2 = st.columns(2)
            with col1:
                cashier_id = st.number_input("Cashier ID", min_value=1, value=22354, help="Unique cashier identifier")
            with col2:
                shift_date = st.date_input("Shift Date", value=date.today())
            
            # st.warning("🚨 **Example:** Cashier 22354 - CONFIRMED 100% risk in training data (27,100% max discrepancy!)")
            
            st.markdown("#### 📊 Balance Difference Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                balance_diff_sum = st.number_input("Balance Diff Sum ($)", value=101066.0, step=100.0, help="Total balance discrepancies")
                balance_diff_mean = st.number_input("Balance Diff Mean ($)", value=66.0, step=1.0, help="Average discrepancy per transaction")
            with col2:
                balance_diff_std = st.number_input("Balance Diff Std Dev ($)", value=150.0, step=1.0, help="Variation in discrepancies (high = suspicious)")
                balance_diff_min = st.number_input("Balance Diff Min ($)", value=-200.0, step=10.0, help="Largest shortage")
            with col3:
                balance_diff_max = st.number_input("Balance Diff Max ($)", value=500.0, step=10.0, help="Largest overage")
                balance_disc_pct_mean = st.number_input("Discrepancy % Mean", value=150.0, step=0.1, help="Average discrepancy percentage")
            
            st.markdown("#### 💰 Transaction Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                balance_disc_pct_max = st.number_input("Discrepancy % Max 🚨", value=27100.0, step=100.0, help="CRITICAL: Maximum discrepancy percentage (model key feature!)")
                trans_total_sum = st.number_input("Transaction Total Sum ($)", value=213647.75, step=100.0, help="Total transaction value")
            with col2:
                trans_total_count = st.number_input("Transaction Count", min_value=1, value=1531, help="Number of transactions")
                trans_total_mean = st.number_input("Transaction Mean ($)", value=139.5, step=1.0, help="Average transaction value")
            with col3:
                vat_sum = st.number_input("VAT Sum ($)", value=32047.16, step=10.0, help="Total VAT collected")
                num_trans_sum = st.number_input("Num Transactions Sum", min_value=1, value=1531, help="Transaction count")
            
            st.markdown("#### 🏦 Balance & Amount Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                opening_bal_mean = st.number_input("Opening Balance Mean ($)", value=1000.0, step=100.0, help="Average shift opening balance")
                closing_bal_mean = st.number_input("Closing Balance Mean ($)", value=50000.0, step=100.0, help="Average shift closing balance")
            with col2:
                id_count = st.number_input("ID Count", min_value=1, value=1, help="Number of unique cashier IDs")
                total_amt_sum = st.number_input("Total Amount Sum ($)", value=213647.75, step=100.0, help="Total amount processed")
            with col3:
                total_amt_mean = st.number_input("Total Amount Mean ($)", value=139.5, step=1.0, help="Average amount per transaction")
                total_amt_std = st.number_input("Total Amount Std Dev ($)", value=85.0, step=1.0, help="Transaction amount variation")
            
            st.markdown("#### 💵 Cash Statistics")
            col1, col2 = st.columns(2)
            with col1:
                cash_amt_sum = st.number_input("Cash Amount Sum ($)", value=150000.0, step=100.0, help="Total cash handled")
            with col2:
                cash_amt_mean = st.number_input("Cash Amount Mean ($)", value=98.0, step=1.0, help="Average cash per transaction")
            
            if st.button("🔍 Analyze Cashier Risk", type="primary"):
                with st.spinner("Analyzing cashier data..."):
                    try:
                        payload = {
                            "cashier_id": cashier_id,
                            "shift_date": shift_date.strftime("%Y-%m-%d"),
                            "balance_diff_sum": balance_diff_sum,
                            "balance_diff_mean": balance_diff_mean,
                            "balance_diff_std": balance_diff_std,
                            "balance_diff_min": balance_diff_min,
                            "balance_diff_max": balance_diff_max,
                            "balance_discrepancy_pct_mean": balance_disc_pct_mean,
                            "balance_discrepancy_pct_max": balance_disc_pct_max,
                            "transaction_total_sum": trans_total_sum,
                            "transaction_total_count": trans_total_count,
                            "transaction_total_mean": trans_total_mean,
                            "vat_component_sum": vat_sum,
                            "num_transactions_sum": num_trans_sum,
                            "opening_balance_mean": opening_bal_mean,
                            "closing_balance_mean": closing_bal_mean,
                            "id_count": id_count,
                            "total_amount_sum": total_amt_sum,
                            "total_amount_mean": total_amt_mean,
                            "total_amount_std": total_amt_std,
                            "cash_amount_sum": cash_amt_sum,
                            "cash_amount_mean": cash_amt_mean
                        }
                        
                        response = requests.post(f"{API_BASE}/api/ml/operations/cashier-risk", json=payload, timeout=30)
                        
                        if response.status_code == 200:
                            res = response.json()
                            if res.get('success'):
                                result = res['data']
                                # Check if model is ready
                                if result.get('status') == 'model_not_ready':
                                    st.warning(f"⚠️ {result.get('message', 'Model not available')}")
                                else:
                                    risk = result.get('risk_assessment', {})
                                    financial = result.get('financial_metrics', {})
                                    operational = result.get('operational_metrics', {})
                                    actions = result.get('recommended_actions', [])
                                    
                                    st.success("✅ Analysis Complete!")
                                    
                                    # Risk Metrics
                                    m1, m2, m3, m4 = st.columns(4)
                                    risk_score = risk.get('risk_score', 0)
                                    m1.metric("Risk Score", f"{risk_score*100:.1f}%")
                                    m2.metric("Risk Level", risk.get('risk_level', 'N/A').upper())
                                    m3.metric("Balance Diff", f"${financial.get('balance_diff_sum', 0):.2f}")
                                    m4.metric("Action Required", "⚠️ Yes" if risk.get('requires_action', False) else "✅ No")
                                    
                                    # Risk visualization
                                    st.markdown("#### 📊 Risk Score")
                                    st.progress(min(risk_score, 1.0))
                                    
                                    # Detailed analysis
                                    st.markdown("---")
                                    col_a, col_b = st.columns(2)
                                    
                                    with col_a:
                                        st.markdown("#### 💰 Financial Metrics")
                                        st.write(f"**Balance Difference Sum:** ${financial.get('balance_diff_sum', 0):.2f}")
                                        st.write(f"**Discrepancy Pct:** {financial.get('balance_discrepancy_pct', 0):.2f}%")
                                        st.write(f"**Transaction Total:** ${financial.get('transaction_total', 0):.2f}")
                                        st.write(f"**Total VAT:** ${financial.get('total_vat', 0):.2f}")
                                    
                                    with col_b:
                                        st.markdown("#### 📋 Operational Metrics")
                                        st.write(f"**Total Transactions:** {operational.get('num_transactions', 0)}")
                                        st.write(f"**Avg Transaction Value:** ${operational.get('avg_transaction_value', 0):.2f}")
                                    
                                    # Recommendations
                                    st.markdown("---")
                                    st.markdown("#### 💡 Recommended Actions")
                                    urgency = risk.get('risk_level', 'low')
                                    if urgency == 'critical':
                                        st.error(f"🚨 **CRITICAL RISK** - Immediate action required")
                                    elif urgency == 'high':
                                        st.warning(f"⚠️ **HIGH RISK** - Review required")
                                    elif urgency == 'medium':
                                        st.info(f"🔵 **MEDIUM RISK** - Monitor closely")
                                    else:
                                        st.success(f"✅ **LOW RISK** - Normal operations")
                                    
                                    for action in actions:
                                        st.write(f"- {action}")
                                    
                                    # Overall assessment
                                    if risk.get('requires_action', False):
                                        st.error("⚠️ **Alert:** Potential operational risk detected. Review recommended.")
                                    else:
                                        st.success("✅ **All Clear:** No significant anomalies detected in this shift.")
                            else:
                                st.error(f"Analysis Error: {res.get('error')}")
                        else:
                            st.error(f"API Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"Could not connect to Cashier Risk model: {str(e)}")
            
        st.markdown("---")
        st.subheader("📋 Batch Analysis")
        st.info("💡 Tip: Use the batch endpoint /api/ml/operations/batch-cashier-risk to analyze multiple shifts at once.")

    
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
        Fresh Flow Markets leverages advanced AI to optimize inventory, reduce waste, and maximize profits for fresh produce departments. Our platform is designed to simplify ordering, casting, and supplier management for retailers of all sizes.
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