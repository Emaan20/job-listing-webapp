# Scraper/scrape.py
import argparse, re, sys, os, time, datetime as dt
from urllib.parse import urljoin

# Make backend importable no matter where we run from
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
for p in (BASE_DIR, BACKEND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.app import create_app
from backend.db import db
from backend.models.job import Job

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

# put near the imports
PROPER_CASE_OVERRIDES = {
    "qbe": "QBE",
    "aig": "AIG",
    "ey": "EY",
    "kpmg": "KPMG",
    "pwc": "PwC",
    "wtw": "WTW",
}

def company_from_slug(url: str) -> str:
    """
    Extract company from /actuarial-jobs/<id>-<company-slug>
    """
    m = re.search(r"/actuarial-jobs/\d+-([a-z0-9\-]+)", url)
    if not m:
        return "Unknown"
    slug = m.group(1)
    if slug in PROPER_CASE_OVERRIDES:
        return PROPER_CASE_OVERRIDES[slug]
    return " ".join(part.capitalize() for part in slug.split("-"))


LISTING_URL = "https://www.actuarylist.com/"

DETAIL_HREF_RE = re.compile(r"/actuarial-jobs/\d+[-/]")  # matches e.g. /actuarial-jobs/20904-liberty-mutual

JOB_TYPE_TERMS = [
    "Intern",
    "Analyst (Entry-Level)",
    "Analyst (Experienced)",
    "Actuary (Associate)",
    "Actuary (Fellow)",
    "Senior Actuary",
]

import datetime as dt
# ...
def parse_relative_date(text: str):
    """
    Return a Python date for strings like '19h ago', '4d ago', '2w ago', '3mo ago'.
    """
    m = re.search(r"(\d+)\s*(h|d|w|mo)\s+ago", text or "", re.I)
    if not m:
        return None
    qty, unit = int(m.group(1)), m.group(2).lower()
    now = dt.datetime.now()
    if unit == "h":
        return now.date()
    if unit == "d":
        return (now - dt.timedelta(days=qty)).date()
    if unit == "w":
        return (now - dt.timedelta(weeks=qty)).date()
    return (now - dt.timedelta(days=qty * 30)).date()  # 'mo' ≈ 30 days

    """
    Convert strings like '19h ago', '1d ago', '4mo ago' to ISO date (YYYY-MM-DD).
    If not found, return None.
    """
    m = re.search(r"(\d+)\s*(h|d|w|mo)\s+ago", text, re.IGNORECASE)
    if not m:
        return None
    qty, unit = int(m.group(1)), m.group(2).lower()
    now = dt.datetime.now()
    if unit == "h":
        dt_val = now - dt.timedelta(hours=qty)
    elif unit == "d":
        dt_val = now - dt.timedelta(days=qty)
    elif unit == "w":
        dt_val = now - dt.timedelta(weeks=qty)
    else:  # 'mo' (roughly 30 days)
        dt_val = now - dt.timedelta(days=qty * 30)
    return dt_val.date().isoformat()

def get_driver(visible: bool = False):
    opts = webdriver.ChromeOptions()
    if not visible:
        # Stable headless mode
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    # Windows font/rendering quirks are okay to ignore
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    except WebDriverException as e:
        print("WebDriver error:", e)
        raise
    driver.set_page_load_timeout(60)
    return driver

def wait_for_any_job_link(driver):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/actuarial-jobs/']"))
    )

def collect_detail_links_on_page(driver) -> list[str]:
    anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/actuarial-jobs/']")
    urls = []
    for a in anchors:
        href = a.get_attribute("href") or ""
        if DETAIL_HREF_RE.search(href):
            urls.append(href)
    # De-dupe but keep order
    seen, unique = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique

def click_next_if_present(driver) -> bool:
    # The listing has a "Next" link at the bottom (we saw "Showing 1 - 30 ... Next")
    # We try a few common patterns.
    for locator in [
        (By.LINK_TEXT, "Next"),
        (By.PARTIAL_LINK_TEXT, "Next"),
        (By.XPATH, "//a[contains(., 'Next')]"),
        (By.CSS_SELECTOR, "a[rel='next']"),
    ]:
        try:
            el = driver.find_element(*locator)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            el.click()
            return True
        except NoSuchElementException:
            continue
        except WebDriverException:
            continue
    return False

from selenium.common.exceptions import NoSuchElementException

def parse_detail(driver, url: str) -> dict | None:
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # --- TITLE: take the H1 (this is the real job title) ---
    try:
        title = driver.find_element(By.XPATH, "//h1").text.strip()
    except NoSuchElementException:
        title = ""

    # --- COMPANY: derive from the slug ---
    company = company_from_slug(url)

    # --- PAGE TEXT for labels like Country, City, Posted Date ---
    text = driver.find_element(By.TAG_NAME, "body").text
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # LOCATION
    city = country = None
    for ln in lines[:120]:
        low = ln.lower()
        if low.startswith("city:"):
            city = ln.split(":", 1)[1].strip()
        elif low.startswith("country:"):
            country = ln.split(":", 1)[1].strip()
        elif "remote" in low and not (city or country):
            country = "Remote"
    if city and country:
        location = f"{city}, {country}"
    else:
        location = country or city or "Remote"

    # POSTED DATE (prefer explicit 'Posted Date:'; else relative 'Xd ago'; else today)
    posting_date = None
    for ln in lines[:150]:
        m = re.search(r"Posted Date:\s*([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})", ln)
        if m:
            try:
                posting_date = dt.datetime.strptime(m.group(1), "%d-%b-%Y").date()
                break
            except Exception:
                pass
        d = parse_relative_date(ln)
        if d and not posting_date:
            posting_date = d
    if not posting_date:
        posting_date = dt.date.today()

    # TAGS (grab the “chips” line close to the top; keep short, dedup)
    tags = []
    for ln in lines[:40]:
        if sum(k in ln for k in ["Analyst", "Actuary", "Life", "Health", "Property",
                                 "Pensions", "Reinsurance", "Python", "SQL", "SAS",
                                 "Pricing", "Risk", "Valuation", "Modelling"]) >= 2:
            parts = re.split(r"[•|,;/\s]+", ln)
            seen = set()
            for p in parts:
                p = p.strip()
                if p and p.lower() not in {"at", "and"} and len(p) <= 30 and p not in seen:
                    tags.append(p)
                    seen.add(p)
            break

    # JOB TYPE (guess from tags; otherwise a safe default)
    job_type = next((t for t in tags if "Actuary" in t or "Analyst" in t), "") or "Analyst (Experienced)"

    # minimal validation
    if not title or not company:
        return None

    return {
        "title": title,
        "company": company,
        "location": location,
        "posting_date": posting_date,  # real date object
        "job_type": job_type,
        "tags": tags,
        "source_url": url,
    }

def upsert_job(sess, data: dict):
    # Ensure posting_date is a Python date
    pd = data.get("posting_date")
    if isinstance(pd, str):
        try:
            pd = dt.date.fromisoformat(pd)
        except Exception:
            pd = dt.date.today()

    existing = (
        sess.query(Job)
        .filter(Job.title == data["title"], Job.company == data["company"], Job.location == data["location"])
        .first()
    )
    if existing:
        existing.posting_date = pd
        existing.job_type = data.get("job_type")
        existing.tags = ",".join(data.get("tags", []))
        sess.add(existing)
        return "updated"
    else:
        j = Job(
            title=data["title"],
            company=data["company"],
            location=data["location"],
            posting_date=pd,
            job_type=data.get("job_type"),
            tags=",".join(data.get("tags", [])),
        )
        sess.add(j)
        return "inserted"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=60, help="max number of jobs to fetch")
    ap.add_argument("--pages", type=int, default=2, help="how many listing pages to walk via Next")
    ap.add_argument("--visible", action="store_true", help="run Chrome with a visible window for debugging")
    args = ap.parse_args()

    app = create_app()
    driver = get_driver(visible=args.visible)

    inserted = updated = skipped = 0
    try:
        driver.get(LISTING_URL)
        wait_for_any_job_link(driver)

        detail_urls = []
        for _ in range(max(1, args.pages)):
            detail_urls.extend(collect_detail_links_on_page(driver))
            # Stop early if we already have enough URLs
            if len(detail_urls) >= args.limit:
                break
            if not click_next_if_present(driver):
                break
            # small wait after pagination
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/actuarial-jobs/']")))

        # unique & trim to limit
        seen, urls = set(), []
        for u in detail_urls:
            if u not in seen:
                seen.add(u)
                urls.append(u)
        urls = urls[: args.limit]

        with app.app_context():
            sess = db.session
            for i, url in enumerate(urls, 1):
                try:
                    data = parse_detail(driver, url)
                    if not data or not data.get("title") or not data.get("company"):
                        skipped += 1
                        continue
                    status = upsert_job(sess, data)
                    if status == "inserted":
                        inserted += 1
                    else:
                        updated += 1
                    if i % 5 == 0:
                        sess.commit()
                except Exception as e:
                    sess.rollback()
                    skipped += 1
                    print(f"[skip] {url}: {e}")
            sess.commit()

    finally:
        driver.quit()

    print(f"Inserted {inserted}, updated {updated}, skipped {skipped}.")

if __name__ == "__main__":
    main()
