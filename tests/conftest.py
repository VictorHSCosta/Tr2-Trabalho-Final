"""Test fixtures for the Flask application."""
import pytest

from app import create_app


@pytest.fixture()
def client():
    """Provide a configured test client for API checks."""
    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as client:
        yield client
