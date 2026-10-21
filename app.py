import os
from flask import Flask, render_template
from config import Config
from routes.main_routes import main_bp
from routes.api_routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Jinja custom filters
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            val = float(value)
            return f"${val:,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    @app.template_filter('comma')
    def comma_filter(value):
        try:
            val = int(value)
            return f"{val:,}"
        except (ValueError, TypeError):
            return "0"

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html', error=str(e)), 500

    return app

app = create_app()

if __name__ == '__main__':
    # Print welcome banner
    print("=" * 65)
    print("   SALES DATA ANALYSIS SYSTEM - COLLEGE PROJECT")
    print("=" * 65)
    print(f" * Server running on: http://127.0.0.1:{Config.PORT}")
    print(" * Ready for CSV Uploads & Sales Analytics")
    print("=" * 65)
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
