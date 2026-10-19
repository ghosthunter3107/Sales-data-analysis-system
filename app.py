import os
from flask import Flask, render_template
from config import Config
from routes.main_routes import main_bp
from routes.api_routes import api_bp
from core.database import test_connection, init_db

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
    print(" * Checking MySQL Database Connection...")
    
    db_ok, db_msg = test_connection()
    if db_ok:
        print(f" [✓] MySQL Connected: {db_msg}")
        init_ok, init_msg = init_db()
        if init_ok:
            print(f" [✓] Tables verified: {init_msg}")
    else:
        print(f" [!] MySQL Notice: {db_msg}")
        print("     The app will run in full preview mode.")
        print("     To connect MySQL, update DB_PASSWORD in .env and restart.")
    
    print("=" * 65)
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
