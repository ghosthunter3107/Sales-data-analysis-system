import pandas as pd
import numpy as np

def filter_dataframe(df, start_date=None, end_date=None, category=None, product=None):
    """
    Filter DataFrame based on provided criteria.
    """
    if df is None or df.empty:
        return df

    filtered = df.copy()

    if start_date:
        filtered = filtered[filtered['Date'] >= str(start_date)]

    if end_date:
        filtered = filtered[filtered['Date'] <= str(end_date)]

    if category and category != "All":
        filtered = filtered[filtered['Category'].astype(str).str.lower() == str(category).lower()]

    if product and product != "All":
        filtered = filtered[filtered['Product'].astype(str).str.lower() == str(product).lower()]

    return filtered

def get_filter_options(df):
    """
    Extract unique categories, products, and date limits for dropdown filters.
    """
    if df is None or df.empty:
        return {
            "categories": [],
            "products": [],
            "min_date": "",
            "max_date": ""
        }

    categories = sorted([c for c in df['Category'].dropna().unique().tolist() if c])
    products = sorted([p for p in df['Product'].dropna().unique().tolist() if p])
    
    dates = pd.to_datetime(df['Date'], errors='coerce').dropna()
    min_date = dates.min().strftime('%Y-%m-%d') if not dates.empty else ""
    max_date = dates.max().strftime('%Y-%m-%d') if not dates.empty else ""

    return {
        "categories": categories,
        "products": products,
        "min_date": min_date,
        "max_date": max_date
    }

def calculate_kpis(df):
    """
    Calculate primary sales KPIs:
    - Total revenue (sum of sales amounts)
    - Total orders (unique Order_ID count)
    - Total units sold (sum of quantities)
    - Average order value (Total revenue / unique orders)
    - Best-selling product (highest units sold)
    - Highest-revenue month (month with highest revenue)
    Safely handles empty datasets and division by zero.
    """
    if df is None or df.empty:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "total_units_sold": 0,
            "average_order_value": 0.0,
            "best_selling_product": {"name": "N/A", "units": 0, "revenue": 0.0},
            "highest_revenue_month": {"month": "N/A", "revenue": 0.0},
            "total_products_count": 0,
            "total_categories_count": 0
        }

    # Total Revenue
    total_revenue = float(round(df['Total_Sales'].sum(), 2))

    # Total Orders (unique Order_ID)
    total_orders = int(df['Order_ID'].nunique())

    # Total Units Sold
    total_units_sold = int(df['Quantity'].sum())

    # Average Order Value (safe division)
    avg_order_value = float(round(total_revenue / total_orders, 2)) if total_orders > 0 else 0.0

    # Best-selling Product (by quantity sold)
    product_agg = df.groupby('Product').agg({
        'Quantity': 'sum',
        'Total_Sales': 'sum'
    }).reset_index()

    if not product_agg.empty:
        best_prod_row = product_agg.loc[product_agg['Quantity'].idxmax()]
        best_selling_product = {
            "name": str(best_prod_row['Product']),
            "units": int(best_prod_row['Quantity']),
            "revenue": float(round(best_prod_row['Total_Sales'], 2))
        }
    else:
        best_selling_product = {"name": "N/A", "units": 0, "revenue": 0.0}

    # Highest-Revenue Month
    temp_df = df.copy()
    temp_df['Year_Month'] = pd.to_datetime(temp_df['Date'], errors='coerce').dt.strftime('%Y-%m')
    temp_df_valid_dates = temp_df.dropna(subset=['Year_Month'])

    if not temp_df_valid_dates.empty:
        month_agg = temp_df_valid_dates.groupby('Year_Month')['Total_Sales'].sum().reset_index()
        top_month_row = month_agg.loc[month_agg['Total_Sales'].idxmax()]
        # Format month to friendly name if possible (e.g. "January 2025")
        try:
            m_dt = pd.to_datetime(top_month_row['Year_Month'] + "-01")
            formatted_month = m_dt.strftime('%B %Y')
        except Exception:
            formatted_month = str(top_month_row['Year_Month'])
            
        highest_revenue_month = {
            "month": formatted_month,
            "raw_month": str(top_month_row['Year_Month']),
            "revenue": float(round(top_month_row['Total_Sales'], 2))
        }
    else:
        highest_revenue_month = {"month": "N/A", "raw_month": "", "revenue": 0.0}

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_units_sold": total_units_sold,
        "average_order_value": avg_order_value,
        "best_selling_product": best_selling_product,
        "highest_revenue_month": highest_revenue_month,
        "total_products_count": int(df['Product'].nunique()),
        "total_categories_count": int(df['Category'].nunique()) if 'Category' in df.columns else 1
    }

def get_charts_data(df):
    """
    Prepares structured JSON-friendly chart datasets for Chart.js:
    - Monthly revenue trend
    - Product-wise revenue
    - Category-wise revenue
    - Top 5 products
    - Sales trends over time (daily/chronological)
    """
    if df is None or df.empty:
        return {
            "monthly_revenue": {"labels": [], "data": []},
            "category_revenue": {"labels": [], "data": []},
            "top_products": {"labels": [], "quantities": [], "revenues": []},
            "sales_trend": {"labels": [], "data": []},
            "category_units": {"labels": [], "data": []}
        }

    work_df = df.copy()
    work_df['Date_Parsed'] = pd.to_datetime(work_df['Date'], errors='coerce')
    work_df = work_df.dropna(subset=['Date_Parsed']).sort_values('Date_Parsed')

    # 1. Monthly Revenue
    work_df['Month_Year'] = work_df['Date_Parsed'].dt.strftime('%b %Y')
    work_df['Sort_Month'] = work_df['Date_Parsed'].dt.strftime('%Y-%m')
    
    monthly_series = work_df.groupby(['Sort_Month', 'Month_Year'])['Total_Sales'].sum().reset_index()
    monthly_series = monthly_series.sort_values('Sort_Month')
    
    monthly_revenue = {
        "labels": monthly_series['Month_Year'].tolist(),
        "data": [round(float(v), 2) for v in monthly_series['Total_Sales']]
    }

    # 2. Category-wise Revenue & Units
    cat_agg = work_df.groupby('Category').agg({
        'Total_Sales': 'sum',
        'Quantity': 'sum'
    }).reset_index().sort_values('Total_Sales', ascending=False)

    category_revenue = {
        "labels": cat_agg['Category'].tolist(),
        "data": [round(float(v), 2) for v in cat_agg['Total_Sales']]
    }

    category_units = {
        "labels": cat_agg['Category'].tolist(),
        "data": [int(v) for v in cat_agg['Quantity']]
    }

    # 3. Top 5 Products by Quantity & Revenue
    prod_agg = work_df.groupby('Product').agg({
        'Quantity': 'sum',
        'Total_Sales': 'sum'
    }).reset_index().sort_values('Quantity', ascending=False).head(5)

    top_products = {
        "labels": prod_agg['Product'].tolist(),
        "quantities": [int(v) for v in prod_agg['Quantity']],
        "revenues": [round(float(v), 2) for v in prod_agg['Total_Sales']]
    }

    # 4. Sales Trend Over Time (Daily aggregation)
    daily_agg = work_df.groupby(work_df['Date_Parsed'].dt.strftime('%Y-%m-%d'))['Total_Sales'].sum().reset_index()
    daily_agg = daily_agg.sort_values('Date_Parsed')
    
    sales_trend = {
        "labels": daily_agg['Date_Parsed'].tolist(),
        "data": [round(float(v), 2) for v in daily_agg['Total_Sales']]
    }

    return {
        "monthly_revenue": monthly_revenue,
        "category_revenue": category_revenue,
        "top_products": top_products,
        "sales_trend": sales_trend,
        "category_units": category_units
    }

def get_breakdown_tables(df):
    """
    Generate category and product performance breakdown tables.
    """
    if df is None or df.empty:
        return {"categories": [], "top_selling": []}

    total_revenue = df['Total_Sales'].sum()

    # Category breakdown
    cat_table = df.groupby('Category').agg({
        'Quantity': 'sum',
        'Total_Sales': 'sum',
        'Order_ID': 'nunique'
    }).reset_index().sort_values('Total_Sales', ascending=False)

    cat_list = []
    for _, row in cat_table.iterrows():
        pct = (row['Total_Sales'] / total_revenue * 100) if total_revenue > 0 else 0
        cat_list.append({
            "category": row['Category'],
            "units": int(row['Quantity']),
            "revenue": round(float(row['Total_Sales']), 2),
            "orders": int(row['Order_ID']),
            "share_percentage": round(float(pct), 1)
        })

    # Product breakdown (Top 10)
    prod_table = df.groupby(['Product', 'Category']).agg({
        'Quantity': 'sum',
        'Price': 'mean',
        'Total_Sales': 'sum'
    }).reset_index().sort_values('Total_Sales', ascending=False).head(10)

    prod_list = []
    for _, row in prod_table.iterrows():
        prod_list.append({
            "product": row['Product'],
            "category": row['Category'],
            "avg_price": round(float(row['Price']), 2),
            "units": int(row['Quantity']),
            "revenue": round(float(row['Total_Sales']), 2)
        })

    return {
        "categories": cat_list,
        "top_selling": prod_list
    }
