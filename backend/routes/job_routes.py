# backend/routes/job_routes.py
from flask import Blueprint, request, jsonify, abort
from datetime import datetime
from sqlalchemy import or_
from backend.db import db
from backend.models.job import Job

job_bp = Blueprint("job_bp", __name__)

@job_bp.get("/jobs")
def list_jobs():
    query = Job.query

    # Filters
    job_type = request.args.get("job_type")
    location = request.args.get("location")
    tag = request.args.get("tag")
    keyword = request.args.get("q")

    if job_type and job_type != "All":
        query = query.filter(Job.job_type == job_type)

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    if tag:
        query = query.filter(Job.tags.ilike(f"%{tag}%"))

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(
                Job.title.ilike(like),
                Job.company.ilike(like),
                Job.location.ilike(like),
                Job.job_type.ilike(like),
                Job.tags.ilike(like),
            )
        )

    # Sorting
    sort = request.args.get("sort", "posting_date_desc")
    if sort == "posting_date_asc":
        query = query.order_by(Job.posting_date.asc().nulls_last())
    elif sort == "title_asc":
        query = query.order_by(Job.title.asc())
    elif sort == "company_asc":
        query = query.order_by(Job.company.asc())
    else:
        query = query.order_by(Job.posting_date.desc().nulls_last())

    # Pagination
    try:
        page = int(request.args.get("page", 1))
        page_size = min(50, max(1, int(request.args.get("page_size", 10))))
    except (TypeError, ValueError):
        page, page_size = 1, 10

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    jobs = [j.to_dict() for j in items]
    return jsonify(jobs=jobs, page=page, page_size=page_size, total=total), 200


@job_bp.get("/jobs/<int:job_id>")
def get_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        abort(404, description="Job not found")
    return jsonify(job=job.to_dict()), 200


@job_bp.post("/jobs")
def create_job():
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    company = (data.get("company") or "").strip()
    location = (data.get("location") or "").strip()

    if not title or not company or not location:
        abort(400, description="title, company, and location are required")

    posting_date = None
    posting_date_str = (data.get("posting_date") or "").strip()
    if posting_date_str:
        try:
            posting_date = datetime.fromisoformat(posting_date_str).date()
        except Exception:
            abort(400, description="posting_date must be a valid date (YYYY-MM-DD)")

    job = Job(
        title=title,
        company=company or "Unknown",
        location=location or "Unknown",
        posting_date=posting_date,
        job_type=(data.get("job_type") or "").strip() or None,
        tags=",".join(data.get("tags") or []) if isinstance(data.get("tags"), list) else (data.get("tags") or None),
        source_url=(data.get("source_url") or "").strip() or None,
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(job=job.to_dict()), 201


@job_bp.put("/jobs/<int:job_id>")
@job_bp.patch("/jobs/<int:job_id>")
def update_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        abort(404, description="Job not found")

    data = request.get_json() or {}

    if "source_url" in data:
        job.source_url = (data.get("source_url") or "").strip() or None

    if "title" in data:
        if not data["title"]:
            abort(400, description="title cannot be empty")
        job.title = data["title"].strip()

    if "company" in data:
        if not data["company"]:
            abort(400, description="company cannot be empty")
        job.company = data["company"].strip()

    if "location" in data:
        if not data["location"]:
            abort(400, description="location cannot be empty")
        job.location = data["location"].strip()

    if "posting_date" in data:
        val = (data.get("posting_date") or "").strip()
        if val:
            try:
                job.posting_date = datetime.fromisoformat(val).date()
            except Exception:
                abort(400, description="posting_date must be a valid date (YYYY-MM-DD)")
        else:
            job.posting_date = None

    if "job_type" in data:
        job.job_type = (data.get("job_type") or "").strip() or None

    if "tags" in data:
        tags = data.get("tags")
        if isinstance(tags, list):
            job.tags = ",".join(tags)
        else:
            job.tags = tags or None

    db.session.commit()
    return jsonify(job=job.to_dict()), 200


@job_bp.delete("/jobs/<int:job_id>")
def delete_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        abort(404, description="Job not found")
    db.session.delete(job)
    db.session.commit()
    return jsonify(message="Job deleted"), 200
