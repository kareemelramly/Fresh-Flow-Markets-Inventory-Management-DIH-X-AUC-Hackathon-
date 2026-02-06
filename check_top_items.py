import sqlite3
import pandas as pd

conn = sqlite3.connect('database/fresh_flow_markets.db')

# Check what categories of items we have with lots of orders
query = """
SELECT 
    i.title,
    COUNT(DISTINCT oi.order_id) as order_count,
    SUM(oi.quantity) as total_quantity
FROM dim_items i
JOIN fct_order_items oi ON i.id = oi.item_id
GROUP BY i.title
HAVING order_count > 1000
ORDER BY order_count DESC
LIMIT 30
"""

df = pd.read_sql_query(query, conn)
print("Top items by order count:")
print(df.to_string(index=False))
conn.close()