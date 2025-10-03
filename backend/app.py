# backend/app.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from urllib.parse import urlsplit, urlunsplit

from db import db
from routes.job_routes import job_bp

load_dotenv()  # local .env; Vercel uses project env vars


def _mask_db_url(url: str) -> str:
    """Mask password in DB URL for safe logging."""
    try:
        parts = urlsplit(url)
        if "@" in parts.netloc and ":" in parts.netloc.split("@", 1)[0]:
            userpass, host = parts.netloc.split("@", 1)
            user, _pwd = userpass.split(":", 1)
            netloc = f"{user}:*****@{host}"
            return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
        return url
    except Exception:
        return url


class StripAPIPrefixMiddleware:
    """
    If a request path starts with '/api', strip it before Flask routing.
    This lets us keep Flask routes at '/jobs' while still serving
    '/api/jobs' on Vercel (and locally if your frontend calls '/api/...').
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path == "/api":
            environ["PATH_INFO"] = "/"
        elif path.startswith("/api/"):
            environ["PATH_INFO"] = path[4:]  # remove leading '/api'
        return self.app(environ, start_response)


def create_app():
    app = Flask(__name__)

    # 1) Database URL (Neon/Supabase/etc) or fallback to sqlite
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_file = os.path.join(base_dir, "jobs.db").replace("\\", "/")
        db_url = f"sqlite:///{db_file}"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Log masked DB URL
    print("DB =", _mask_db_url(db_url))

    # 2) CORS
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
    CORS(
        app,
        resources={
            r"/jobs*": {"origins": frontend_origin if frontend_origin != "*" else "*"},
            r"/api/*": {"origins": frontend_origin if frontend_origin != "*" else "*"},
        }
    )

    # 3) DB init
    db.init_app(app)
    if os.getenv("DB_AUTO_CREATE") == "1":
        with app.app_context():
            db.create_all()

    # 4) Register routes at '/jobs' (no '/api' inside Flask)
    app.register_blueprint(job_bp, url_prefix="")

    # 5) Health check (Vercel will expose it at /api/health)
    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    # 6) Middleware to support '/api/*' paths seamlessly
    app.wsgi_app = StripAPIPrefixMiddleware(app.wsgi_app)

    return app


if __name__ == "__main__":
    # Local dev: both /jobs and /api/jobs will work (middleware strips /api)
    app = create_app()
    app.run(debug=True)
