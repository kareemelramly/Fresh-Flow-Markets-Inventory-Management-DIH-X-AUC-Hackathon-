# business_trends_content.py
"""
Business Trends content for Fresh Flow Markets dashboard.
Includes key findings, recommendations, and visualization descriptions from business analysis.
"""

business_trends_sections = [
    {
        'title': 'Customer Loyalty Analysis',
        'description': '''
Customer loyalty is driven by understanding order patterns, segmenting customers, and targeting VIPs. The following visuals help identify peak sales periods, spending habits, and the value of VIP customers. Use these insights to optimize campaign timing and retention strategies.
''',
        'images': [
            {'file': 'Inventory Management business analysis/Customer Loyalty Analysis/visualizations/01_orders_by_day.png', 'caption': 'Orders by Day of Week', 'desc': 'Shows which days have the highest order volume. Friday is the peak, ideal for campaign launches.'},
            {'file': 'Inventory Management business analysis/Customer Loyalty Analysis/visualizations/02_orders_by_hour.png', 'caption': 'Orders by Hour of Day', 'desc': 'Reveals hourly order patterns. Lunch hours (11 AM - 2 PM) are busiest.'},
            {'file': 'Inventory Management business analysis/Customer Loyalty Analysis/visualizations/05_vip_vs_regular.png', 'caption': 'VIP vs Regular Customer Comparison', 'desc': 'VIPs spend over twice as much as regular customers. Target VIPs for premium offers.'},
            {'file': 'Inventory Management business analysis/Customer Loyalty Analysis/visualizations/07_campaign_timing_heatmap.png', 'caption': 'Campaign Timing Heatmap', 'desc': 'Visualizes order volume by day and hour. Friday midday is optimal for marketing.'},
            {'file': 'Inventory Management business analysis/Customer Loyalty Analysis/visualizations/08_segment_performance.png', 'caption': 'RFM Segment Performance Metrics', 'desc': 'Champions and Loyal segments drive the highest value. Focus retention efforts here.'}
        ]
    },
    {
        'title': 'Operational Marketing & Pricing Analysis',
        'description': '''
Operational efficiency and pricing strategies are key to maximizing revenue and customer satisfaction. These visuals highlight staff performance, processing times, and the impact of discounts and marketing campaigns.
''',
        'images': [
            {'file': 'Inventory Management business analysis/Operational Marketing & Pricing Analysis/visualizations/processing_time_analysis.png', 'caption': 'Processing Time Analysis', 'desc': 'Average processing time exceeds 1 hour. Optimize kitchen workflow and add staff during peak hours.'},
            {'file': 'Inventory Management business analysis/Operational Marketing & Pricing Analysis/visualizations/staff_performance_analysis.png', 'caption': 'Staff Performance Analysis', 'desc': 'Staff performance varies widely. Training can standardize and improve service.'},
            {'file': 'Inventory Management business analysis/Operational Marketing & Pricing Analysis/visualizations/pricing_revenue_analysis.png', 'caption': 'Pricing & Revenue Analysis', 'desc': 'Most revenue comes from orders with no discount. Focus promotions in this range.'},
            {'file': 'Inventory Management business analysis/Operational Marketing & Pricing Analysis/visualizations/marketing_efficiency_analysis.png', 'caption': 'Marketing Efficiency Analysis', 'desc': 'Bonus code usage is low. Improve awareness and restructure codes for larger orders.'}
        ]
    },
    {
        'title': 'Other Insights',
        'description': 'Additional business analysis visuals. These images may show operational layouts, user flows, or other supporting data. Use them for deeper operational reviews or presentations.',
        'images': [
            {'file': 'Inventory Management business analysis/other/other_files/image003.png', 'caption': 'Operational Layout Example', 'desc': 'Shows a typical operational layout for process optimization.'},
            {'file': 'Inventory Management business analysis/other/other_files/image004.png', 'caption': 'User Flow Diagram', 'desc': 'Illustrates user flow through the ordering process.'},
            {'file': 'Inventory Management business analysis/other/other_files/image005.png', 'caption': 'Additional Operational Insight', 'desc': 'Provides further detail for operational review.'}
        ]
    }
]
