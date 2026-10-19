import re
import pymysql
from pymysql.cursors import DictCursor
from config import Config

def get_connection(use_database=True):
    """
    Establish a connection to the MySQL database.
    If use_database is False, connects to the MySQL server without selecting a specific database.
    """
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME if use_database else None,
        cursorclass=DictCursor,
        connect_timeout=3,
        autocommit=True
    )

def test_connection():
    """
    Test connection to MySQL server.
    Returns (status: bool, message: str)
    """
    try:
        conn = get_connection(use_database=False)
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version;")
            row = cursor.fetchone()
            version = row['version'] if row else "Unknown"
        conn.close()
        return True, f"Successfully connected to MySQL (Version: {version})"
    except pymysql.err.OperationalError as e:
        code, msg = e.args if len(e.args) >= 2 else (0, str(e))
        if code == 1045:
            return False, "Access Denied: Incorrect MySQL username or password in .env file."
        elif code == 2003:
            return False, "Can't connect to MySQL server on localhost:3306. Check if MySQL service is running."
        else:
            return False, f"MySQL Operational Error ({code}): {msg}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def init_db():
    """
    Initialize the sales_analysis database and create tables if not present.
    Returns (status: bool, message: str)
    """
    try:
        conn = get_connection(use_database=False)
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` DEFAULT CHARACTER SET utf8mb4;")
            cursor.execute(f"USE `{Config.DB_NAME}`;")
            
            # Products table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id VARCHAR(50) PRIMARY KEY,
                product_name VARCHAR(150) NOT NULL UNIQUE,
                category VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Sales transactions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id VARCHAR(50) NOT NULL UNIQUE,
                product_name VARCHAR(150) NOT NULL,
                category VARCHAR(100) NOT NULL,
                sale_date DATE NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                total_sales DECIMAL(12, 2) NOT NULL,
                region VARCHAR(50) DEFAULT 'General',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_order_id (order_id),
                INDEX idx_sale_date (sale_date),
                INDEX idx_category (category),
                INDEX idx_product_name (product_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
        conn.close()
        return True, f"Database `{Config.DB_NAME}` and tables verified successfully."
    except Exception as e:
        return False, f"Failed to initialize database: {str(e)}"

def save_sales_records(df):
    """
    Insert cleaned DataFrame records into MySQL tables.
    Prevents duplicates on order_id.
    Returns dict with inserted count, duplicates/skipped count, and error if any.
    """
    if df is None or df.empty:
        return {"inserted": 0, "skipped": 0, "error": "No records to insert."}
    
    # Ensure database and tables exist
    init_ok, init_msg = init_db()
    if not init_ok:
        return {"inserted": 0, "skipped": 0, "error": init_msg}

    inserted_count = 0
    skipped_count = 0

    try:
        conn = get_connection(use_database=True)
        with conn.cursor() as cursor:
            # 1. Update/insert unique products
            product_dict = {}
            for _, row in df.iterrows():
                pname = str(row['Product']).strip()
                cat = str(row.get('Category', 'General')).strip()
                if pname and pname not in product_dict:
                    # Generate simple product id slug e.g. PRD-MOUSE
                    slug = "PRD-" + re.sub(r'[^A-Za-z0-9]', '', pname)[:10].upper()
                    product_dict[pname] = (slug, pname, cat)
            
            for slug, pname, cat in product_dict.values():
                cursor.execute("""
                    INSERT INTO products (product_id, product_name, category)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE category = VALUES(category);
                """, (slug, pname, cat))

            # 2. Insert sales records (preventing duplicate order_id)
            for _, row in df.iterrows():
                order_id = str(row['Order_ID']).strip()
                pname = str(row['Product']).strip()
                cat = str(row.get('Category', 'General')).strip()
                # Ensure date format is YYYY-MM-DD
                sale_date = str(row['Date'])[:10]
                qty = int(row['Quantity'])
                price = float(row['Price'])
                total = float(row['Total_Sales'])
                region = str(row.get('Region', 'General')).strip()

                # Use INSERT IGNORE to skip existing duplicates
                sql = """
                    INSERT IGNORE INTO sales 
                    (order_id, product_name, category, sale_date, quantity, unit_price, total_sales, region)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                affected = cursor.execute(sql, (order_id, pname, cat, sale_date, qty, price, total, region))
                if affected > 0:
                    inserted_count += 1
                else:
                    skipped_count += 1

        conn.close()
        return {
            "inserted": inserted_count,
            "skipped": skipped_count,
            "total_processed": len(df),
            "error": None
        }
    except Exception as e:
        return {"inserted": inserted_count, "skipped": skipped_count, "error": str(e)}

def get_all_sales(limit=100, offset=0, search=None, category=None, start_date=None, end_date=None):
    """
    Retrieve sales records from MySQL with search and filters.
    Returns (records: list, total_count: int, error: str or None)
    """
    try:
        conn = get_connection(use_database=True)
        conditions = []
        params = []

        if search:
            conditions.append("(order_id LIKE %s OR product_name LIKE %s OR category LIKE %s OR region LIKE %s)")
            wild = f"%{search}%"
            params.extend([wild, wild, wild, wild])
        
        if category and category != "All":
            conditions.append("category = %s")
            params.append(category)

        if start_date:
            conditions.append("sale_date >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("sale_date <= %s")
            params.append(end_date)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with conn.cursor() as cursor:
            # Count total matching
            count_sql = f"SELECT COUNT(*) AS total FROM sales {where_clause};"
            cursor.execute(count_sql, tuple(params))
            total_count = cursor.fetchone()['total']

            # Retrieve records
            query_sql = f"""
                SELECT sale_id, order_id, product_name, category, 
                       DATE_FORMAT(sale_date, '%%Y-%%m-%%d') AS sale_date,
                       quantity, unit_price, total_sales, region
                FROM sales
                {where_clause}
                ORDER BY sale_date DESC, sale_id DESC
                LIMIT %s OFFSET %s;
            """
            cursor.execute(query_sql, tuple(params + [limit, offset]))
            records = cursor.fetchall()

        conn.close()
        return records, total_count, None
    except Exception as e:
        return [], 0, str(e)

def get_database_stats():
    """
    Calculate summary stats directly from MySQL database.
    Returns (stats: dict, error: str or None)
    """
    try:
        conn = get_connection(use_database=True)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT order_id) AS total_orders,
                    COALESCE(SUM(quantity), 0) AS total_units,
                    COALESCE(SUM(total_sales), 0.0) AS total_revenue,
                    COUNT(DISTINCT product_name) AS unique_products,
                    MIN(sale_date) AS min_date,
                    MAX(sale_date) AS max_date
                FROM sales;
            """)
            stats = cursor.fetchone()
        conn.close()
        return stats, None
    except Exception as e:
        return None, str(e)

def get_categories_list():
    """Retrieve distinct categories from MySQL table."""
    try:
        conn = get_connection(use_database=True)
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT category FROM sales ORDER BY category;")
            rows = cursor.fetchall()
        conn.close()
        return [r['category'] for r in rows if r['category']]
    except Exception:
        return []
