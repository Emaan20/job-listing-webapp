# backend/models/job.py
from datetime import datetime
# RIGHT
from db import db



class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    posting_date = db.Column(db.Date, nullable=True)
    job_type = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.Text, nullable=True)             # comma-separated
    source_url = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # avoid exact duplicates
    __table_args__ = (
        db.UniqueConstraint("title", "company", "location", name="uq_jobs_title_company_location"),
    )

    def to_dict(self):
        """Serialize for API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "posting_date": self.posting_date.isoformat() if self.posting_date else None,
            "job_type": self.job_type,
            "tags": self.tags.split(",") if self.tags else [],
            "source_url": self.source_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
