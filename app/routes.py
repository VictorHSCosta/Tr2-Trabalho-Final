"""Application routes."""
from flask import Blueprint, jsonify, render_template

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    """Render the initial HTML page."""
    return render_template("index.html")


@bp.get("/api/health")
def health() -> tuple[dict[str, str], int]:
    """Simple health endpoint useful for API tests."""
    return jsonify({"status": "ok"}), 200
