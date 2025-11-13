"""
WarpTPS FastAPI Server

This module provides a RESTful API server for WarpTPS image warping operations.
Install server dependencies with: pip install warptps[server]
Run the server with: python -m warptps.server
"""

from .main import app

__all__ = ["app"]
