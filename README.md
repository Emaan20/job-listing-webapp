# Job Listing Web App (Flask + React + Selenium)

A clean, beginner‑friendly full‑stack project that lists actuarial jobs. Backend is a Flask REST API
with SQLAlchemy; frontend is React (Vite); and a Selenium scraper seeds the database.

## Project Structure
This follows your required layout exactly (note: `requirement.txt` name kept):  
```txt
project-root/
├── backend/
│   ├── app.py
│   ├── db.py
│   ├── config.py
│   ├── models/
│   │   └── job.py
│   ├── routes/
│   │   └── job_routes.py
│   └── requirement.txt
├── Scraper/
│   └── scrape.py
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── App.css
    │   ├── App.jsx
    │   ├── api.js
    │   ├── index.jsx
    │   └── components/
    │       ├── FilterBar.jsx
    │       ├── JobCard.jsx
    │       └── JobList.jsx
    └── package.json
```

---
## 1) Backend Setup (Flask API)

### Option A: Quick start with SQLite (no DB install)
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirement.txt
python app.py  # runs on http://127.0.0.1:5000
```

### Option B: Use PostgreSQL/MySQL
Set `DATABASE_URL` env var. Examples:
- Postgres: `export DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/jobs`
- MySQL:    `export DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/jobs`

Then run `python app.py`.

#### API Examples
- List (with filters): `GET /api/jobs?job_type=Full-time&location=London&tag=Pricing&sort=posting_date_desc`
- Create:
  ```json
  POST /api/jobs
  { "title":"Analyst", "company":"Acme", "location":"London", "posting_date":"2025-10-02",
    "job_type":"Full-time", "tags":["Life","Pricing"] }
  ```
- Update: `PUT /api/jobs/1`
- Delete: `DELETE /api/jobs/1`

---
## 2) Frontend Setup (React)

We use Vite for a fast dev experience (you may swap to CRA if you prefer).
```bash
cd frontend
npm i
npm run dev   # http://127.0.0.1:5173
```
Create a `.env` file with the API base if needed:
```
VITE_API_BASE=http://127.0.0.1:5000/api
```

---
## 3) Run the Selenium Scraper

The scraper inserts jobs directly into the same database as the backend.
```bash
cd Scraper
# Ensure backend virtualenv deps installed already (selenium/webdriver-manager included there)
python scrape.py --limit 60
```
If selectors change on the site, open `scrape.py` and tweak the CSS/XPath noted in comments.

---
## 4) Common Gotchas

- **CORS**: Already enabled via `Flask-Cors` in `app.py`.
- **Dates**: Frontend uses `YYYY-MM-DD`. Backend accepts ISO. Invalid dates are rejected with 400.
- **Tags**: Stored as comma‑separated in the DB; displayed as chips.
- **Dedupe** (scraper): by `title+company+location` combo.
- **Env**: If using Postgres/MySQL, set `DATABASE_URL` before running the scraper too.

---
## 5) What to Show in Your Video
1. `GET/POST/PUT/DELETE` on `/api/jobs` in Postman or browser.
2. Frontend listing jobs, adding, editing, deleting, filtering and sorting.
3. Run `python Scraper/scrape.py --limit 20` and refresh frontend to see new jobs.
4. Briefly walk through code structure and your choices.
