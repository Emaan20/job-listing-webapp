# backend/api/index.py
from app import create_app

# Vercel looks for a module-level WSGI `app`
app = create_app()
