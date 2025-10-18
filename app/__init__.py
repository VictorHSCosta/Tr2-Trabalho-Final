"""Application factory for the Flask project."""
from flask import Flask


def create_app() -> Flask:
    """Build the core Flask application."""
    app = Flask(__name__)

    from .routes import bp as main_bp  # local import to avoid circular deps

    app.register_blueprint(main_bp)
    return app
