#!/usr/bin/env python3
"""
Startup script for AskAI API.

This script provides a simple way to start the AskAI API server
for development and testing purposes.
"""
import os
import sys
import argparse

# Add project paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from askai.presentation.api.app import create_app


def main():
    """Main entry point for the API server."""
    parser = argparse.ArgumentParser(description='Start the AskAI API server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1, use 0.0.0.0 for all interfaces)')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--config', help='Path to configuration file')

    args = parser.parse_args()

    # Warn if binding to all interfaces
    if args.host == '0.0.0.0':
        print("⚠️  Warning: Binding to all interfaces (0.0.0.0). Ensure this is intended and secure.")

    # Set environment variables
    os.environ['FLASK_HOST'] = args.host
    os.environ['FLASK_PORT'] = str(args.port)
    os.environ['FLASK_DEBUG'] = str(args.debug).lower()

    if args.config:
        os.environ['ASKAI_CONFIG_PATH'] = args.config

    # Create and run the app
    app = create_app()

    print("Starting AskAI API server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Debug: {args.debug}")
    print(f"Swagger UI: http://{args.host}:{args.port}/docs/")
    print(f"API Base URL: http://{args.host}:{args.port}/api/v1/")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()