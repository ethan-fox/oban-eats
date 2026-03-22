"""
Application entry point.
Used by all deployment modes (API, Worker, etc.).
"""
from src.app import create_app

app = create_app()
