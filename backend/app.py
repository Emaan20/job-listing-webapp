# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
from backend.db import db
from backend.routes.job_routes import job_bp
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    # Use DATABASE_URL from env if present; else fall back to jobs.db in project root
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_file = os.path.join(base_dir, "jobs.db")
        db_url = f"sqlite:///{db_file.replace('\\', '/')}"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Print masked DB URL  for debug
    print("DB =", db_url.replace(os.getenv("YourStrongPassword123", ""), "*****"))

    CORS(app)  

    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(job_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
