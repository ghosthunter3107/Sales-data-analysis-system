import pandas as pd
import numpy as np

# Standardized expected column names
STANDARD_COLUMNS = {
    'order_id': 'Order_ID',
    'date': 'Date',
    'product': 'Product',
    'category': 'Category',
    'quantity': 'Quantity',
    'price': 'Price',
    'total_sales': 'Total_Sales',
    'region': 'Region'
}

# Synonyms for auto-mapping
COLUMN_ALIASES = {
    'order_id': ['order_id', 'order id', 'orderid', 'sale_id', 'sale id', 'id', 'transaction_id'],
    'date': ['date', 'order_date', 'order date', 'sale_date', 'sale date', 'timestamp'],
    'product': ['product', 'product_name', 'product name', 'item', 'item_name', 'item name'],
    'category': ['category', 'product_category', 'item_category', 'department'],
    'quantity': ['quantity', 'qty', 'units', 'quantity_sold', 'units_sold'],
    'price': ['price', 'unit_price', 'unit price', 'rate', 'cost'],
    'total_sales': ['total_sales', 'total sales', 'total', 'sales', 'revenue', 'amount', 'total_amount'],
    'region': ['region', 'location', 'zone', 'area', 'city']
}

def map_and_standardize_columns(df):
    """
    Standardize DataFrame column names using fuzzy/synonym matching.
    Returns (standardized_df, column_mapping_dict, missing_required_columns).
    """
    df_cols = list(df.columns)
    mapping = {}
    
    # Clean column strings (lowercase, strip whitespace, remove underscores)
    normalized_file_cols = {col: str(col).strip().lower().replace('_', ' ') for col in df_cols}
    
    for original_col, norm in normalized_file_cols.items():
        norm_no_space = norm.replace(' ', '')
        matched = False
        for std_key, target_col in STANDARD_COLUMNS.items():
            aliases = COLUMN_ALIASES.get(std_key, [std_key])
            for alias in aliases:
                alias_norm = alias.replace('_', ' ')
                alias_no_space = alias.replace('_', '').replace(' ', '')
                if norm == alias_norm or norm_no_space == alias_no_space:
                    mapping[original_col] = target_col
                    matched = True
                    break
            if matched:
                break
                
    mapped_df = df.rename(columns=mapping)
    
    # Required columns for a valid sales analysis
    required = ['Order_ID', 'Date', 'Product', 'Quantity', 'Price']
    missing_required = [col for col in required if col not in mapped_df.columns]
    
    return mapped_df, mapping, missing_required

def inspect_dataset(df):
    """
    Inspects raw DataFrame for quality issues:
    - Missing values
    - Duplicate rows and duplicate Order_IDs
    - Invalid numbers (negative quantities or prices)
    - Unparseable dates
    - Inconsistent Total_Sales calculations
    """
    issues = []
    total_rows = len(df)
    
    if total_rows == 0:
        return {
            "total_rows": 0,
            "issues": ["The uploaded file contains no data rows."],
            "summary": {"duplicates": 0, "missing_cells": 0, "invalid_rows": 0, "mismatched_sales": 0}
        }
        
    # Check duplicate rows
    duplicate_rows_count = int(df.duplicated().sum())
    duplicate_order_ids_count = 0
    if 'Order_ID' in df.columns:
        duplicate_order_ids_count = int(df['Order_ID'].dropna().duplicated().sum())
        
    if duplicate_rows_count > 0:
        issues.append(f"Found {duplicate_rows_count} exact duplicate row(s).")
    if duplicate_order_ids_count > duplicate_rows_count:
        issues.append(f"Found {duplicate_order_ids_count} duplicate Order_ID values across distinct rows.")
        
    # Check missing values per column
    missing_counts = df.isnull().sum().to_dict()
    total_missing_cells = sum(missing_counts.values())
    for col, count in missing_counts.items():
        if count > 0:
            issues.append(f"Column '{col}' has {count} missing value(s).")
            
    # Check Quantity
    invalid_quantities = 0
    if 'Quantity' in df.columns:
        for idx, val in df['Quantity'].items():
            if pd.isna(val):
                continue
            try:
                num = float(val)
                if num <= 0 or not num.is_integer():
                    invalid_quantities += 1
            except (ValueError, TypeError):
                invalid_quantities += 1
        if invalid_quantities > 0:
            issues.append(f"Column 'Quantity' has {invalid_quantities} invalid or non-positive value(s).")

    # Check Price
    invalid_prices = 0
    if 'Price' in df.columns:
        for idx, val in df['Price'].items():
            if pd.isna(val):
                continue
            try:
                num = float(val)
                if num <= 0:
                    invalid_prices += 1
            except (ValueError, TypeError):
                invalid_prices += 1
        if invalid_prices > 0:
            issues.append(f"Column 'Price' has {invalid_prices} invalid or non-positive value(s).")

    # Check Date parsing
    invalid_dates = 0
    if 'Date' in df.columns:
        converted = pd.to_datetime(df['Date'], errors='coerce')
        invalid_dates = int(converted.isna().sum() - df['Date'].isna().sum())
        if invalid_dates > 0:
            issues.append(f"Column 'Date' has {invalid_dates} unparseable date value(s).")

    # Check Total_Sales consistency
    mismatched_sales = 0
    if 'Quantity' in df.columns and 'Price' in df.columns and 'Total_Sales' in df.columns:
        for idx, row in df.iterrows():
            try:
                q = float(row['Quantity'])
                p = float(row['Price'])
                t = float(row['Total_Sales'])
                expected = q * p
                if abs(t - expected) > 0.05:
                    mismatched_sales += 1
            except (ValueError, TypeError):
                pass
        if mismatched_sales > 0:
            issues.append(f"Found {mismatched_sales} row(s) where Total_Sales does not match Quantity × Price.")

    return {
        "total_rows": total_rows,
        "issues": issues,
        "summary": {
            "duplicates": duplicate_rows_count,
            "duplicate_order_ids": duplicate_order_ids_count,
            "missing_cells": total_missing_cells,
            "invalid_quantities": invalid_quantities,
            "invalid_prices": invalid_prices,
            "invalid_dates": invalid_dates,
            "mismatched_sales": mismatched_sales
        }
    }

def clean_and_sanitize_dataframe(df):
    """
    Cleans raw DataFrame using documented policies:
    1. Remove exact duplicate rows and duplicate Order_IDs (keeping the first valid occurrence).
    2. Convert Date to standard YYYY-MM-DD; drop rows with completely invalid dates.
    3. Ensure Quantity is positive integer; drop malformed quantities.
    4. Ensure Price is positive float; drop malformed prices.
    5. Calculate or correct Total_Sales = Quantity * Price.
    6. Fill missing Category with 'General' and missing Region with 'General'.
    7. Strip extraneous whitespaces from string columns.
    
    Returns (cleaned_df, cleaning_report).
    """
    raw_count = len(df)
    report = {
        "initial_rows": raw_count,
        "duplicates_removed": 0,
        "invalid_rows_removed": 0,
        "sales_recalculated": 0,
        "categories_filled": 0,
        "final_rows": 0,
        "actions": []
    }
    
    if raw_count == 0:
        report["final_rows"] = 0
        return df, report

    # Make working copy
    clean_df = df.copy()

    # 1. Strip string whitespace
    for col in clean_df.select_dtypes(include=['object', 'string']):
        clean_df[col] = clean_df[col].astype(str).str.strip()

    # 2. Drop exact duplicate rows
    initial_before_dups = len(clean_df)
    clean_df = clean_df.drop_duplicates()
    dups_removed = initial_before_dups - len(clean_df)
    
    # Also deduplicate on Order_ID if present
    if 'Order_ID' in clean_df.columns:
        dups_order_id = int(clean_df.duplicated(subset=['Order_ID']).sum())
        clean_df = clean_df.drop_duplicates(subset=['Order_ID'], keep='first')
        dups_removed += dups_order_id

    report["duplicates_removed"] = dups_removed
    if dups_removed > 0:
        report["actions"].append(f"Removed {dups_removed} duplicate record(s).")

    # 3. Handle missing Category & Region defaults
    if 'Category' not in clean_df.columns:
        clean_df['Category'] = 'General'
        report["actions"].append("Added missing 'Category' column with default value 'General'.")
    else:
        empty_cat = clean_df['Category'].isna() | (clean_df['Category'] == '') | (clean_df['Category'] == 'nan')
        filled_cat_count = int(empty_cat.sum())
        if filled_cat_count > 0:
            clean_df.loc[empty_cat, 'Category'] = 'General'
            report["categories_filled"] = filled_cat_count
            report["actions"].append(f"Filled {filled_cat_count} empty Category values with 'General'.")

    if 'Region' not in clean_df.columns:
        clean_df['Region'] = 'General'
    else:
        empty_reg = clean_df['Region'].isna() | (clean_df['Region'] == '') | (clean_df['Region'] == 'nan')
        clean_df.loc[empty_reg, 'Region'] = 'General'

    # 4. Standardize Date
    initial_len = len(clean_df)
    clean_df['Parsed_Date'] = pd.to_datetime(clean_df['Date'], errors='coerce')
    # Filter rows with valid dates
    valid_dates_mask = clean_df['Parsed_Date'].notna()
    invalid_dates_dropped = int((~valid_dates_mask).sum())
    clean_df = clean_df[valid_dates_mask].copy()
    clean_df['Date'] = clean_df['Parsed_Date'].dt.strftime('%Y-%m-%d')
    clean_df.drop(columns=['Parsed_Date'], inplace=True)
    
    if invalid_dates_dropped > 0:
        report["actions"].append(f"Removed {invalid_dates_dropped} row(s) with unparseable dates.")

    # 5. Validate and Clean Quantity
    clean_df['Quantity_Clean'] = pd.to_numeric(clean_df['Quantity'], errors='coerce')
    valid_qty_mask = clean_df['Quantity_Clean'].notna() & (clean_df['Quantity_Clean'] > 0)
    invalid_qty_dropped = int((~valid_qty_mask).sum())
    clean_df = clean_df[valid_qty_mask].copy()
    clean_df['Quantity'] = clean_df['Quantity_Clean'].astype(int)
    clean_df.drop(columns=['Quantity_Clean'], inplace=True)

    if invalid_qty_dropped > 0:
        report["actions"].append(f"Removed {invalid_qty_dropped} row(s) with invalid or negative Quantity.")

    # 6. Validate and Clean Price
    clean_df['Price_Clean'] = pd.to_numeric(clean_df['Price'], errors='coerce')
    valid_price_mask = clean_df['Price_Clean'].notna() & (clean_df['Price_Clean'] > 0)
    invalid_price_dropped = int((~valid_price_mask).sum())
    clean_df = clean_df[valid_price_mask].copy()
    clean_df['Price'] = clean_df['Price_Clean'].round(2)
    clean_df.drop(columns=['Price_Clean'], inplace=True)

    if invalid_price_dropped > 0:
        report["actions"].append(f"Removed {invalid_price_dropped} row(s) with invalid or non-positive Price.")

    # Total invalid rows removed
    report["invalid_rows_removed"] = invalid_dates_dropped + invalid_qty_dropped + invalid_price_dropped

    # 7. Calculate or Correct Total_Sales
    recalculated = 0
    calculated_total = (clean_df['Quantity'] * clean_df['Price']).round(2)
    
    if 'Total_Sales' not in clean_df.columns:
        clean_df['Total_Sales'] = calculated_total
        recalculated = len(clean_df)
        report["actions"].append("Generated 'Total_Sales' column (Quantity × Price) for all rows.")
    else:
        clean_df['Total_Sales_Num'] = pd.to_numeric(clean_df['Total_Sales'], errors='coerce')
        # Check discrepancy
        diff = (clean_df['Total_Sales_Num'] - calculated_total).abs()
        mismatch_mask = clean_df['Total_Sales_Num'].isna() | (diff > 0.05)
        recalculated = int(mismatch_mask.sum())
        clean_df['Total_Sales'] = calculated_total
        clean_df.drop(columns=['Total_Sales_Num'], inplace=True)
        if recalculated > 0:
            report["actions"].append(f"Recalculated Total_Sales for {recalculated} row(s) where values were missing or mismatched.")

    report["sales_recalculated"] = recalculated

    # Ensure Order_ID and Product are non-empty strings
    clean_df = clean_df[clean_df['Order_ID'].astype(str).str.len() > 0]
    clean_df = clean_df[clean_df['Product'].astype(str).str.len() > 0]

    report["final_rows"] = len(clean_df)
    if report["final_rows"] == raw_count and not report["actions"]:
        report["actions"].append("Dataset is 100% clean and consistent! No modifications were needed.")

    # Reorder columns logically
    final_cols = ['Order_ID', 'Date', 'Product', 'Category', 'Quantity', 'Price', 'Total_Sales']
    if 'Region' in clean_df.columns:
        final_cols.append('Region')
    
    # Retain any extra columns safely
    for col in clean_df.columns:
        if col not in final_cols:
            final_cols.append(col)

    clean_df = clean_df[final_cols].reset_index(drop=True)
    return clean_df, report
