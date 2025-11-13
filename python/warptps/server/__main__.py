"""
CLI entry point for WarpTPS server.

Usage:
    python -m warptps.server [--host HOST] [--port PORT]

Example:
    python -m warptps.server --host 0.0.0.0 --port 8000
"""

import argparse
import sys

try:
    import uvicorn
except ImportError:
    print("Error: Server dependencies not installed.", file=sys.stderr)
    print("Install with: pip install warptps[server]", file=sys.stderr)
    sys.exit(1)

from .main import app


def main():
    parser = argparse.ArgumentParser(
        description="WarpTPS FastAPI Server - Thin Plate Spline image warping API"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    print(f"Starting WarpTPS API Server on {args.host}:{args.port}")
    print(f"API documentation available at: http://{args.host}:{args.port}/docs")

    uvicorn.run(
        "warptps.server.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
