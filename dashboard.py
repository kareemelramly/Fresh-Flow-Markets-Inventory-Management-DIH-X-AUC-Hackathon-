import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# API Configuration
API_BASE = "http://localhost:5000"

def fetch_data(endpoint, params=None):
    try:
        response = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                return data
        return None
    except:
        return None

def safe_columns(df, required_cols):
    available_cols = [col for col in required_cols if col in df.columns]
    return df[available_cols] if available_cols else df

# Page configuration (GLOBAL - only once at top)
st.set_page_config(
    page_title="Fresh Flow Markets",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
with st.sidebar:
    st.title("Fresh Flow Markets")
    st.markdown("---")
    
    # Page selection
    page = st.radio(
        "Navigate to:",
        ["Main Statistics", "Inventory Management", "Forecasting Suggestions"]
    )
    
    st.markdown("---")
    st.caption("Deloitte x AUC Hackathon")

# MAIN CONTENT - All functions defined BEFORE being called
def show_dashboard():
    """Main Statistics Dashboard - called only when page == "Main Statistics" """
    st.title("📊 Fresh Flow Markets - Sales Dashboard")

    # --- 1. DATA FETCHING ---
    with st.spinner("Fetching latest data..."):
        analytics = fetch_data("/api/analytics/dashboard")
        orders_meta = fetch_data("/api/orders", params={"per_page": 1})

    # --- 2. KPI CALCULATIONS ---
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

    # --- 3. METRIC CARDS ---
    st.subheader("🎯 Key Business Metrics")
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Total Transactions", f"{total_orders:,}")
    with m2: 
        rev_str = f"${total_revenue:,.2f}" if total_revenue < 1000000 else f"${total_revenue/1000000:.2f}M"
        st.metric("Total Revenue", rev_str)
    with m3: st.metric("Average Order Value", f"${aov:.2f}")

    st.divider()

    # --- 4. ORDER STATUS METRICS ---
    st.subheader("📦 Order Counts by Status")
    status_data = []
    if analytics and 'data' in analytics:
        status_data = analytics['data'].get('by_status', [])
    
    if status_data:
        df_status = pd.DataFrame(status_data)
        cols = st.columns(min(4, len(df_status)))
        for idx, status_row in enumerate(df_status.itertuples()):
            with cols[idx % len(cols)]:
                count = status_row.count
                status_name = status_row.status.replace('_', ' ').title()
                st.metric(status_name, f"{count:,}")
    
    st.divider()

    # --- 5. ORDER STATUS PIE CHART ---
    st.subheader("📊 Order Status Distribution")
    if status_data:
        df_status = pd.DataFrame(status_data)
        col_pie, col_stat_table = st.columns([2, 1])
        with col_pie:
            fig_pie = px.pie(df_status, values='count', names='status', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_stat_table:
            st.dataframe(df_status, use_container_width=True, hide_index=True)

    st.divider()

    # --- 6. TOP SELLING ITEMS ---
    st.subheader("🏆 Top Selling Items")
    top_items_raw = analytics['data'].get('top_items', []) if analytics and 'data' in analytics else []

    if top_items_raw:
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

    if st.button("🔄 Refresh Dashboard", type="primary"):
        st.rerun()

def show_inventory():
    """Inventory Management - YOUR SPECIFIC CODE BLOCK """
    st.title("📦 Inventory Items Dashboard")
    st.markdown("**Manage stock levels and item performance**")

    # Sidebar - only appears on inventory page
    st.sidebar.header("⚙️ Filters")
    per_page = st.sidebar.selectbox("Items per page", [10, 20, 50], index=1)
    search_term = st.sidebar.text_input("Search Items")

    # Tabs - only appear on inventory page
    tab1, tab2, tab3 = st.tabs(["📋 All Items", "📈 Top Sellers", "📊 Inventory Stats"])
    
  

# Page routing
if page == "Main Statistics":
    show_dashboard()
elif page == "Inventory Management":
    show_inventory()
elif page == "Forecasting Suggestions":
    st.title("🔮 Forecasting Suggestions")
    st.write("Forecasting suggestions page")
