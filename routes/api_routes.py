from flask import Blueprint, jsonify, request
from core import data_store
from core.analyzer import calculate_kpis, get_charts_data, filter_dataframe, get_breakdown_tables

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/status')
def status():
    """Returns system status and active dataset state."""
    active_data = data_store.get_active_dataset()
    
    return jsonify({
        "status": "online",
        "dataset": {
            "has_data": data_store.has_active_data(),
            "filename": active_data.get('filename'),
            "is_cleaned": (active_data.get('cleaned_df') is not None),
            "rows": len(data_store.get_working_df()) if data_store.has_active_data() else 0
        }
    })

@api_bp.route('/charts-data')
def charts_data_api():
    """Returns dynamically filtered JSON data for Chart.js."""
    working_df = data_store.get_working_df()
    if working_df is None or working_df.empty:
        return jsonify({
            "error": "No dataset loaded",
            "monthly_revenue": {"labels": [], "data": []},
            "category_revenue": {"labels": [], "data": []},
            "top_products": {"labels": [], "quantities": [], "revenues": []},
            "sales_trend": {"labels": [], "data": []},
            "category_units": {"labels": [], "data": []}
        })

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    product = request.args.get('product')

    filtered_df = filter_dataframe(
        working_df, 
        start_date=start_date, 
        end_date=end_date, 
        category=category, 
        product=product
    )

    data = get_charts_data(filtered_df)
    data["kpis"] = calculate_kpis(filtered_df)
    data["filtered_rows"] = len(filtered_df)
    data["total_rows"] = len(working_df)
    return jsonify(data)
