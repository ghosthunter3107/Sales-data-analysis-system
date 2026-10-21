"""
Database module (Disabled).
The application operates entirely in-memory using Pandas and CSV datasets.
MySQL dependencies and connections have been disabled.
"""

def test_connection():
    return False, "Database connection is disabled. Running in CSV / In-Memory mode."

def init_db():
    return True, "No database initialization required."

def save_sales_records(df):
    return {"inserted": 0, "skipped": 0, "error": None}

def get_all_sales(*args, **kwargs):
    return [], 0, None

def get_database_stats():
    return {"total_records": 0, "total_revenue": 0, "total_products": 0}, None

def get_categories_list():
    return []
