import pytest
import pandas as pd
from core.analyzer import (
    calculate_kpis,
    filter_dataframe,
    get_charts_data,
    get_breakdown_tables
)

@pytest.fixture
def sample_sales_df():
    data = {
        'Order_ID': ['ORD-1', 'ORD-2', 'ORD-3', 'ORD-4'],
        'Date': ['2025-01-10', '2025-01-20', '2025-02-05', '2025-02-15'],
        'Product': ['Mouse', 'Keyboard', 'Mouse', 'Monitor'],
        'Category': ['Electronics', 'Electronics', 'Electronics', 'Electronics'],
        'Quantity': [5, 2, 10, 1],
        'Price': [20.0, 50.0, 20.0, 300.0],
        'Total_Sales': [100.0, 100.0, 200.0, 300.0]
    }
    return pd.DataFrame(data)

def test_kpi_formulas(sample_sales_df):
    """Verify all 6 core formulas match mathematical definitions."""
    kpis = calculate_kpis(sample_sales_df)

    # 1. Total revenue = sum of valid sales amounts: 100 + 100 + 200 + 300 = 700.0
    assert kpis['total_revenue'] == 700.0

    # 2. Total orders = unique orders count: 4
    assert kpis['total_orders'] == 4

    # 3. Total units sold = sum of valid quantities: 5 + 2 + 10 + 1 = 18
    assert kpis['total_units_sold'] == 18

    # 4. Average order value = total revenue / unique orders: 700 / 4 = 175.0
    assert kpis['average_order_value'] == 175.0

    # 5. Best-selling product = product with highest units sold: Mouse (5 + 10 = 15 units)
    assert kpis['best_selling_product']['name'] == 'Mouse'
    assert kpis['best_selling_product']['units'] == 15
    assert kpis['best_selling_product']['revenue'] == 300.0

    # 6. Highest-revenue month: Feb 2025 (200 + 300 = 500 vs Jan 200)
    assert 'February 2025' in kpis['highest_revenue_month']['month']
    assert kpis['highest_revenue_month']['revenue'] == 500.0

def test_empty_dataset_safety():
    """Verify that an empty DataFrame does not raise DivisionByZero or IndexError."""
    empty_df = pd.DataFrame(columns=['Order_ID', 'Date', 'Product', 'Category', 'Quantity', 'Price', 'Total_Sales'])
    kpis = calculate_kpis(empty_df)

    assert kpis['total_revenue'] == 0.0
    assert kpis['total_orders'] == 0
    assert kpis['total_units_sold'] == 0
    assert kpis['average_order_value'] == 0.0
    assert kpis['best_selling_product']['name'] == 'N/A'
    assert kpis['highest_revenue_month']['month'] == 'N/A'

def test_filtering_logic(sample_sales_df):
    """Verify filtering by product, category, and date range."""
    # Filter by Product
    filtered_prod = filter_dataframe(sample_sales_df, product='Mouse')
    assert len(filtered_prod) == 2
    assert set(filtered_prod['Product']) == {'Mouse'}

    # Filter by Date range (only Feb)
    filtered_date = filter_dataframe(sample_sales_df, start_date='2025-02-01', end_date='2025-02-28')
    assert len(filtered_date) == 2
    assert 'ORD-3' in list(filtered_date['Order_ID'])
    assert 'ORD-4' in list(filtered_date['Order_ID'])

def test_charts_data_structure(sample_sales_df):
    """Verify charts payload has correct keys and array types for Chart.js."""
    charts = get_charts_data(sample_sales_df)

    assert 'monthly_revenue' in charts
    assert 'labels' in charts['monthly_revenue']
    assert 'data' in charts['monthly_revenue']
    assert len(charts['monthly_revenue']['labels']) == 2  # Jan & Feb

    assert 'category_revenue' in charts
    assert 'top_products' in charts
    assert 'sales_trend' in charts
