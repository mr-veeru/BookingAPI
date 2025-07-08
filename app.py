"""
Main Flask application for the Booking API.
Creates the Flask app, registers blueprints, and handles startup.
"""
from flask import Flask
from db import get_db_connection, init_db
from routes.classes import classes_bp
from routes.bookings import bookings_bp
from routes.admin import admin_bp
from config import DevelopmentConfig  # Use DevelopmentConfig by default
import logging
import os


def create_app(test_conn=None) -> Flask:
    """
    Application factory for the Booking API.
    Registers blueprints and initializes the database connection.
    Loads configuration from config.py.
    """
    app = Flask(__name__)
    # Load config (can be overridden by environment variable if desired)
    app.config.from_object(os.environ.get(
        'BOOKINGAPI_CONFIG', 'config.DevelopmentConfig'))
    conn = test_conn or get_db_connection()
    app.config['DB_CONN'] = conn

    # Basic logging
    logging.basicConfig(level=logging.INFO)

    # Register blueprints
    app.register_blueprint(classes_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(admin_bp)

    # Root route
    @app.route('/')
    def root():
        return 'Welcome to Booking API'

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"error": "Internal server error"}, 500

    return app


if __name__ == '__main__':
    conn = get_db_connection()
    init_db(conn)
    app = create_app(test_conn=conn)
    app.run(debug=True)
