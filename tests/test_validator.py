import pytest
import pandas as pd
from core.validator import (
    map_and_standardize_columns,
    inspect_dataset,
    clean_and_sanitize_dataframe
)

def test_column_mapping_aliases():
    """Verify that columns with alternative casing or names map correctly."""
    data = {
        'order id': ['ORD-1', 'ORD-2'],
        'order_date': ['2025-01-01', '2025-01-02'],
        'item_name': ['Mouse', 'Keyboard'],
        'qty': [2, 1],
        'unit_price': [25.0, 50.0],
        'department': ['Electronics', 'Electronics']
    }
    df = pd.DataFrame(data)
    mapped_df, mapping, missing = map_and_standardize_columns(df)

    assert 'Order_ID' in mapped_df.columns
    assert 'Date' in mapped_df.columns
    assert 'Product' in mapped_df.columns
    assert 'Quantity' in mapped_df.columns
    assert 'Price' in mapped_df.columns
    assert 'Category' in mapped_df.columns
    assert len(missing) == 0

def test_missing_required_columns():
    """Verify error flag when required columns are missing."""
    data = {
        'Order_ID': ['ORD-1'],
        'Product': ['Laptop']
    }
    df = pd.DataFrame(data)
    _, _, missing = map_and_standardize_columns(df)
    assert 'Date' in missing
    assert 'Quantity' in missing
    assert 'Price' in missing

def test_inspect_dataset_detects_issues():
    """Verify inspection audit catches bad dates, negative values, and mismatched sales."""
    dirty_data = {
        'Order_ID': ['ORD-1', 'ORD-2', 'ORD-3', 'ORD-1'],
        'Date': ['2025-01-01', 'bad-date', '2025-01-03', '2025-01-01'],
        'Product': ['Mouse', 'Chair', 'Desk', 'Mouse'],
        'Category': ['Electronics', 'Furniture', 'Furniture', 'Electronics'],
        'Quantity': [2, -1, 3, 2],
        'Price': [20.0, 50.0, -10.0, 20.0],
        'Total_Sales': [40.0, 50.0, 999.0, 40.0]  # Row 3 has mismatch
    }
    df = pd.DataFrame(dirty_data)
    audit = inspect_dataset(df)

    assert audit['summary']['duplicates'] == 1
    assert audit['summary']['invalid_dates'] >= 1
    assert audit['summary']['invalid_quantities'] >= 1
    assert audit['summary']['invalid_prices'] >= 1
    assert audit['summary']['mismatched_sales'] >= 1

def test_clean_and_sanitize_dataframe():
    """Verify cleaning policy removes duplicates, bad rows, and recalculates Total_Sales."""
    dirty_data = {
        'Order_ID': ['ORD-1', 'ORD-2', 'ORD-3', 'ORD-4', 'ORD-1'],
        'Date': ['2025-01-01', 'not-a-date', '2025-01-03', '2025-01-04', '2025-01-01'],
        'Product': ['Mouse', 'Desk', 'Keyboard', 'Monitor', 'Mouse'],
        'Category': ['Electronics', 'Furniture', None, 'Electronics', 'Electronics'],
        'Quantity': [2, 1, 3, -5, 2],
        'Price': [25.0, 100.0, 50.0, 200.0, 25.0],
        'Total_Sales': [50.0, 100.0, 10.0, -1000.0, 50.0]  # ORD-3 has mismatched total
    }
    df = pd.DataFrame(dirty_data)
    clean_df, report = clean_and_sanitize_dataframe(df)

    # ORD-1: Duplicate removed
    # ORD-2: Bad date removed
    # ORD-4: Negative quantity removed
    # ORD-3: Missing Category filled with 'General', Total_Sales recalculated to 3 * 50 = 150.0
    assert report['duplicates_removed'] >= 1
    assert report['invalid_rows_removed'] >= 2
    assert report['sales_recalculated'] >= 1

    # Remaining valid row is ORD-3 and ORD-1
    assert len(clean_df) == 2
    ord3_row = clean_df[clean_df['Order_ID'] == 'ORD-3'].iloc[0]
    assert ord3_row['Category'] == 'General'
    assert ord3_row['Total_Sales'] == 150.0
