# api/index.py
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app import create_app

app = create_app()  # vercel will serve this WSGI app
