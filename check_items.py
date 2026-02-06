import sqlite3
conn = sqlite3.connect('database/fresh_flow_markets.db')
cursor = conn.cursor()
cursor.execute("SELECT id, title FROM dim_items WHERE id IN (59856, 59857, 59858) OR title LIKE '%Sodavand%' OR title LIKE '%Cola%' LIMIT 20")
results = cursor.fetchall()
for r in results:
    print(f"{r[0]}: {r[1]}")
conn.close()