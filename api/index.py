# Serverless wrapper for your existing Flask app on Vercel
import os
import sys

# Make "backend" importable when running in /api
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.app import create_app  # your existing app factory

# IMPORTANT: Do *not* enable debug or built-in reloader here.
flask_app = create_app()

# Vercel's Python runtime looks for a global variable named "app" or "handler".
# Expose the Flask WSGI app as "app".
app = flask_app
