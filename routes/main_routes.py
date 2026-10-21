import io
import os
from pathlib import Path
import pandas as pd
from flask import (
    Blueprint, render_template, request, redirect, url_for, 
    flash, send_file, Response, current_app
)
from werkzeug.utils import secure_filename

from config import Config, BASE_DIR
from core import data_store
from core.validator import (
    map_and_standardize_columns,
    inspect_dataset,
    clean_and_sanitize_dataframe
)
from core.analyzer import (
    calculate_kpis,
    get_charts_data,
    get_breakdown_tables,
    filter_dataframe,
    get_filter_options
)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home landing page."""
    # Check if data is currently loaded in memory
    active_data = data_store.get_active_dataset()
    has_data = data_store.has_active_data()
    working_df = data_store.get_working_df()
    
    # Calculate preview stats if data available
    preview_kpis = None
    if has_data and working_df is not None:
        preview_kpis = calculate_kpis(working_df)

    return render_template(
        'index.html',
        has_data=has_data,
        filename=active_data.get('filename'),
        preview_kpis=preview_kpis,
        is_cleaned=(active_data.get('cleaned_df') is not None)
    )

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """CSV Upload and preview page."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part selected. Please select a CSV file.', 'warning')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected. Please choose a CSV file.', 'warning')
            return redirect(request.url)

        if not file.filename.lower().endswith('.csv'):
            flash('Invalid file format. Only .csv files are supported.', 'danger')
            return redirect(request.url)

        try:
            # Read CSV safely with pandas
            # Support various encodings
            content = file.read()
            if len(content) == 0:
                flash('The uploaded file is empty.', 'danger')
                return redirect(request.url)
                
            try:
                raw_df = pd.read_csv(io.BytesIO(content), encoding='utf-8')
            except UnicodeDecodeError:
                raw_df = pd.read_csv(io.BytesIO(content), encoding='latin1')

            # Standardize and map columns
            mapped_df, mapping_used, missing_cols = map_and_standardize_columns(raw_df)

            if missing_cols:
                flash(
                    f"CSV is missing required columns: {', '.join(missing_cols)}. "
                    f"Detected columns: {list(raw_df.columns)}", 
                    'danger'
                )
                return redirect(request.url)

            # Store in session data store
            filename = secure_filename(file.filename) or "uploaded_sales.csv"
            data_store.set_raw_dataset(mapped_df, filename=filename, source='upload')
            
            # Run audit inspection
            audit = inspect_dataset(mapped_df)
            data_store.set_validation_report(audit)

            flash(f"Successfully uploaded '{filename}' with {len(mapped_df)} rows and {len(mapped_df.columns)} columns!", 'success')
            return redirect(url_for('main.validation'))

        except Exception as e:
            flash(f"Error processing CSV file: {str(e)}", 'danger')
            return redirect(request.url)

    # GET request
    active_data = data_store.get_active_dataset()
    raw_df = active_data.get('raw_df')
    preview_rows = []
    columns = []
    row_count = 0
    col_count = 0

    if raw_df is not None and not raw_df.empty:
        row_count = len(raw_df)
        col_count = len(raw_df.columns)
        columns = list(raw_df.columns)
        preview_rows = raw_df.head(10).to_dict(orient='records')

    return render_template(
        'upload.html',
        has_data=(raw_df is not None and not raw_df.empty),
        filename=active_data.get('filename'),
        row_count=row_count,
        col_count=col_count,
        columns=columns,
        preview_rows=preview_rows
    )

@main_bp.route('/load-sample/<dataset_name>')
def load_sample(dataset_name):
    """Load pre-packaged sample dataset for instant demonstration."""
    sample_files = {
        'clean': BASE_DIR / 'sample_data' / 'sample_sales.csv',
        'issues': BASE_DIR / 'sample_data' / 'sample_sales_with_issues.csv'
    }
    
    file_path = sample_files.get(dataset_name)
    if not file_path or not file_path.exists():
        flash('Sample dataset not found.', 'danger')
        return redirect(url_for('main.upload'))

    raw_df = pd.read_csv(file_path)
    mapped_df, _, _ = map_and_standardize_columns(raw_df)
    
    data_store.set_raw_dataset(
        mapped_df, 
        filename=file_path.name, 
        source='sample'
    )
    audit = inspect_dataset(mapped_df)
    data_store.set_validation_report(audit)

    flash(f"Loaded sample dataset '{file_path.name}' ({len(mapped_df)} rows).", 'info')
    return redirect(url_for('main.validation'))

@main_bp.route('/validation')
def validation():
    """Data Validation and Quality Audit page."""
    active_data = data_store.get_active_dataset()
    raw_df = active_data.get('raw_df')

    if raw_df is None or raw_df.empty:
        flash('Please upload or load a CSV dataset first.', 'warning')
        return redirect(url_for('main.upload'))

    # Run or fetch audit
    audit = active_data.get('validation_report')
    if not audit:
        audit = inspect_dataset(raw_df)
        data_store.set_validation_report(audit)

    cleaned_df = active_data.get('cleaned_df')
    cleaning_report = active_data.get('cleaning_report')

    # Preview rows
    display_df = cleaned_df if cleaned_df is not None else raw_df
    preview_rows = display_df.head(15).to_dict(orient='records')
    columns = list(display_df.columns)

    return render_template(
        'validation.html',
        filename=active_data.get('filename'),
        audit=audit,
        is_cleaned=(cleaned_df is not None),
        cleaning_report=cleaning_report,
        preview_rows=preview_rows,
        columns=columns,
        total_rows=len(display_df)
    )

@main_bp.route('/clean', methods=['POST'])
def clean_data():
    """Trigger the data cleaning and sanitation engine."""
    active_data = data_store.get_active_dataset()
    raw_df = active_data.get('raw_df')

    if raw_df is None or raw_df.empty:
        flash('No raw dataset found to clean.', 'warning')
        return redirect(url_for('main.upload'))

    cleaned_df, report = clean_and_sanitize_dataframe(raw_df)
    data_store.set_cleaned_dataset(cleaned_df, report)

    flash(
        f"Data Cleaning Complete: {report['initial_rows']} initial rows → "
        f"{report['final_rows']} clean rows ready for analysis!",
        'success'
    )
    return redirect(url_for('main.validation'))

@main_bp.route('/dashboard')
def dashboard():
    """Sales Analysis Dashboard with KPI cards and interactive filters."""
    working_df = data_store.get_working_df()

    if working_df is None or working_df.empty:
        flash('No dataset loaded. Please upload a CSV file or load sample data.', 'info')
        return redirect(url_for('main.upload'))

    # Extract filter options from the working dataset
    filter_opts = get_filter_options(working_df)

    # Get query parameters for filtering
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    category = request.args.get('category', 'All')
    product = request.args.get('product', 'All')

    # Apply filters
    filtered_df = filter_dataframe(
        working_df, 
        start_date=start_date, 
        end_date=end_date, 
        category=category, 
        product=product
    )

    # Compute KPIs
    kpis = calculate_kpis(filtered_df)

    # Breakdown tables
    breakdown = get_breakdown_tables(filtered_df)

    return render_template(
        'dashboard.html',
        kpis=kpis,
        filter_opts=filter_opts,
        current_filters={
            'start_date': start_date,
            'end_date': end_date,
            'category': category,
            'product': product
        },
        breakdown=breakdown,
        filtered_rows=len(filtered_df),
        total_rows=len(working_df)
    )

@main_bp.route('/charts')
def charts():
    """Visual Analytics and Interactive Charts page."""
    working_df = data_store.get_working_df()

    if working_df is None or working_df.empty:
        flash('No dataset loaded. Please upload a CSV or load a sample first.', 'info')
        return redirect(url_for('main.upload'))

    filter_opts = get_filter_options(working_df)

    # Check filter args
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    category = request.args.get('category', 'All')

    filtered_df = filter_dataframe(
        working_df,
        start_date=start_date,
        end_date=end_date,
        category=category
    )

    charts_data = get_charts_data(filtered_df)

    return render_template(
        'charts.html',
        charts_data=charts_data,
        filter_opts=filter_opts,
        current_filters={
            'start_date': start_date,
            'end_date': end_date,
            'category': category
        },
        filtered_rows=len(filtered_df),
        total_rows=len(working_df)
    )

@main_bp.route('/database')
def database_view():
    """Redirect database visits to dashboard."""
    return redirect(url_for('main.dashboard'))

@main_bp.route('/database/save', methods=['POST'])
def save_to_database():
    """Redirect legacy database save to dashboard."""
    return redirect(url_for('main.dashboard'))

@main_bp.route('/download/cleaned')
def download_cleaned():
    """Download cleaned dataset as CSV."""
    active_data = data_store.get_active_dataset()
    cleaned_df = active_data.get('cleaned_df')

    if cleaned_df is None or cleaned_df.empty:
        flash('No cleaned dataset available for download.', 'warning')
        return redirect(url_for('main.validation'))

    csv_data = cleaned_df.to_csv(index=False)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=cleaned_sales_data.csv"}
    )
