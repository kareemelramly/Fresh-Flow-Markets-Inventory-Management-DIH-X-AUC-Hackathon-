"""
Database connection utilities
"""

import sqlite3
from flask import current_app, g
import pandas as pd

def get_db():
    """Get database connection from Flask g object"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """Execute a query and return results as list of dicts"""
    cur = get_db().execute(query, args)
    rv = [dict(row) for row in cur.fetchall()]
    cur.close()
    return (rv[0] if rv else None) if one else rv

def query_df(query, args=()):
    """Execute a query and return results as pandas DataFrame"""
    conn = get_db()
    return pd.read_sql_query(query, conn, params=args)

def execute_db(query, args=()):
    """Execute a write query (INSERT, UPDATE, DELETE)"""
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()
    return cursor.lastrowid
