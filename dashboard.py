import streamlit as st
import pandas as pd
import requests
import plotly.express as px

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

# --- NEW TOP NAVIGATION ---
# --- TOP NAVIGATION ADJUSTMENT ---

st.markdown(
    """
    <style>
        /* Adjust page top padding */
        .block-container {
            padding-top: 3.5rem; 
        }
        
        /* Style buttons to look like clickable text labels */
        div.stButton > button {
            border: none;
            background-color: transparent;
            color: #FAFAFA; /* Matches default light text, adjust if needed */
            padding: 0;
            font-size: 16px;
            font-weight: 400;
        }
        
        /* Remove hover border/background */
        div.stButton > button:hover {
            color: #FF4B4B; /* Changes color on hover */
            background-color: transparent;
            border: none;
        }

        /* Active state/focus styling */
        div.stButton > button:focus {
            color: #FF4B4B;
            background-color: transparent;
            box-shadow: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for page routing if it doesn't exist
if 'page' not in st.session_state:
    st.session_state.page = "Main Statistics"

# Create clickable text links using columns
nav_col1, nav_col2, nav_col3, _ = st.columns([1.5, 2, 2, 5])

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
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_stat_table:
            st.dataframe(df_status, use_container_width=True, hide_index=True)
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
            st.plotly_chart(fig, use_container_width=True)
        with col_table:
            st.dataframe(df_top, use_container_width=True, hide_index=True)
    else:
        st.info("📊 No top selling items data available")

    if st.button("🔄 Refresh Dashboard", type="primary"):
        st.rerun()

def show_inventory():
    """Inventory Management Page"""
    st.title("📦 Inventory Management")
    st.markdown("**Monitor and manage your inventory items**")

    # Use variables from the conditional sidebar defined at top
    params = {
        'page': page_num,
        'per_page': per_page
    }
    if search_term:
        params['search'] = search_term

    data = fetch_data('/api/inventory/items', params)
    
    if data and data.get('data'):
        items = data['data']
        pagination = data.get('pagination', {})
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.info(f"📊 Showing {len(items)} items | Page {pagination.get('page', 1)} of {pagination.get('pages', 1)} | Total: {pagination.get('total', 0)}")
        
        df = pd.DataFrame(items)
        tab1, tab2, tab3 = st.tabs(["📋 All Items", "📊 Item Details", "🔍 Quick Search"])
        
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
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        
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
            st.subheader("Quick Search")
            st.markdown("Use the search box in the sidebar to filter items by name or barcode")
            st.info("💡 Tip: Try searching for 'Sodavand', 'Øl', or any item name")
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
    tab1, tab2, tab3 = st.tabs(["📈 Demand Forecast", "📦 Reorder Recommendations", "🔄 Bulk Forecast"])
    
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
                                cols = st.columns(3)
                                with cols[0]: st.metric("Current Price", f"${item_info.get('current_price', 0):.2f}")
                                with cols[1]: st.metric("Current Stock", item_info.get('current_stock', 'N/A'))
                                with cols[2]: st.metric("Minimum Stock", item_info.get('minimum_stock', 'N/A'))
                            
                            st.subheader("Forecast Results")
                            cols = st.columns(3)
                            with cols[0]: st.metric("Predicted Demand", f"{forecast_data.get('predicted_demand', 0):.1f} units")
                            with cols[1]: st.metric("Confidence Level", f"{forecast_data.get('confidence', 0):.0%}")
                            with cols[2]: st.metric("Recommendation", forecast_data.get('recommendation', 'N/A'))
                            
                            if 'daily_forecast' in forecast_data:
                                daily_df = pd.DataFrame(forecast_data['daily_forecast'])
                                fig = px.line(daily_df, x='date', y='predicted_quantity', title=f'{forecast_days}-Day Demand Forecast')
                                st.plotly_chart(fig, use_container_width=True)
                                st.dataframe(daily_df, use_container_width=True, hide_index=True)
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
                            cols = st.columns(4)
                            with cols[0]: st.metric("Reorder Quantity", f"{reorder_data.get('reorder_quantity', 0):.0f}")
                            with cols[1]: st.metric("Reorder Point", f"{reorder_data.get('reorder_point', 0):.0f}")
                            with cols[2]: st.metric("Safety Stock", f"{reorder_data.get('safety_stock', 0):.0f}")
                            with cols[3]: st.metric("Days Until Reorder", f"{reorder_data.get('days_until_reorder', 0):.0f}")
                            if 'recommendation' in reorder_data: st.info(f"💡 {reorder_data['recommendation']}")
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
                        summary_data = [{'Item ID': f.get('item_id'), 'Predicted Demand': f"{f.get('predicted_demand', 0):.1f}", 'Confidence': f"{f.get('confidence', 0):.0%}", 'Recommendation': f.get('recommendation', 'N/A')} for f in forecasts]
                        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
            except Exception as e: st.error(f"Error: {str(e)}")

# Page routing
if page == "Main Statistics":
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