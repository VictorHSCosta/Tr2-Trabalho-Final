"""Flask application entry point."""
from app import create_app

app = create_app()


if __name__ == "__main__":
    # Debug mode is handy for development; disable it for production deployments.
    app.run(debug=True)
