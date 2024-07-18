import sqlite3
from datetime import datetime, timedelta

def create_run_history_table():
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS run_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 run_time TEXT)''')

    conn.commit()
    conn.close()

def initialize_database():
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS job_listings
                 (id TEXT PRIMARY KEY,
                 title TEXT,
                 company TEXT,
                 location TEXT,
                 published TEXT,
                 salary TEXT,
                 summary TEXT,
                 link TEXT,
                 description TEXT,
                 sponsorship_checked INTEGER,
                 candidate_fit_checked INTEGER,
                 inactive INTEGER,
                 created_at TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS run_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 run_time TEXT)''')
    create_run_history_table()

    conn.commit()
    conn.close()

def save_job_listings(job_listings):
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    for job in job_listings:
        c.execute("""
            INSERT OR IGNORE INTO job_listings (id, title, company, location, published, salary, summary, link, description, sponsorship_checked, candidate_fit_checked, inactive, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (job['id'], job['title'], job['company'], job['location'], job['published'], job['salary'], job['summary'], job['link'], job['description'], job['sponsorship_checked'], job['candidate_fit_checked'], 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

def get_last_run_time():
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    c.execute("SELECT run_time FROM run_history ORDER BY id DESC LIMIT 1")
    result = c.fetchone()

    conn.close()

    if result:
        return datetime.strptime(result[0], "%a, %d %b %Y %H:%M:%S %Z")
    else:
        return None

def update_job_listing_checked(job_id, field):
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    if field == 'candidate_fit':
        c.execute("UPDATE job_listings SET candidate_fit_checked = 1 WHERE id = ?", (job_id,))
    elif field == 'sponsorship':
        c.execute("UPDATE job_listings SET sponsorship_checked = 1 WHERE id = ?", (job_id,))
    else:
        raise ValueError("Invalid field. Must be 'candidate_fit' or 'sponsorship'.")

    conn.commit()
    conn.close()

def load_all_job_listings_filtered(filter_type):
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    if filter_type == 'sponsorship':
        c.execute("SELECT * FROM job_listings WHERE sponsorship_checked = 0 AND inactive = 0")
    elif filter_type == 'candidate_fit':
        c.execute("SELECT * FROM job_listings WHERE candidate_fit_checked = 0 AND inactive = 0")
    elif filter_type == 'all':
        c.execute("SELECT * FROM job_listings WHERE inactive = 0")
    else:
        raise ValueError("Invalid filter type. Must be 'sponsorship', 'candidate_fit', or 'all'.")

    result = c.fetchall()
    job_listings = []

    for row in result:
        job = {
            'id': row[0],
            'title': row[1],
            'company': row[2],
            'location': row[3],
            'published': row[4],
            'salary': row[5],
            'summary': row[6],
            'link': row[7],
            'description': row[8],
            'sponsorship_checked': bool(row[9]),
            'candidate_fit_checked': bool(row[10]),
            'inactive': bool(row[11]),
            'created_at': row[12]
        }
        job_listings.append(job)

    conn.close()

    return job_listings

def load_job_listings(status='ready', job_id=None):
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    if job_id:
        c.execute("SELECT * FROM job_listings WHERE id = ?", (job_id,))
    elif status == 'ready':
        c.execute("SELECT * FROM job_listings WHERE sponsorship_checked = 1 AND candidate_fit_checked = 1 AND inactive = 0 ORDER BY published ASC LIMIT 1")
    elif status == 'unchecked':
        c.execute("SELECT * FROM job_listings WHERE (sponsorship_checked = 0 OR candidate_fit_checked = 0) AND inactive = 0 ORDER BY published ASC LIMIT 1")
    else:
        c.execute("SELECT * FROM job_listings WHERE inactive = 0 ORDER BY published ASC LIMIT 1")

    result = c.fetchone()

    if result:
        job = {
            'id': result[0],
            'title': result[1],
            'company': result[2],
            'location': result[3],
            'published': result[4],
            'salary': result[5],
            'summary': result[6],
            'link': result[7],
            'description': result[8],
            'sponsorship_checked': bool(result[9]),
            'candidate_fit_checked': bool(result[10]),
            'inactive': bool(result[11]),
            'created_at': result[12]
        }
        return [job]
    else:
        return []

def get_job_listing_stats():
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM job_listings WHERE inactive = 0")
    total_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM job_listings WHERE (sponsorship_checked = 0 OR candidate_fit_checked = 0) AND inactive = 0")
    unchecked_count = c.fetchone()[0]

    ready_count = total_count - unchecked_count

    stats = {
        'total_count': total_count,
        'unchecked_count': unchecked_count,
        'ready_count': ready_count
    }

    conn.close()

    return stats

def mark_job_listing_inactive(job_id):
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    c.execute("UPDATE job_listings SET inactive = 1 WHERE id = ?", (job_id,))

    conn.commit()
    conn.close()

def prune_old_job_listings():
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    thirty_days_ago = datetime.now() - timedelta(days=30)
    c.execute("DELETE FROM job_listings WHERE created_at < ?", (thirty_days_ago.strftime("%Y-%m-%d %H:%M:%S"),))

    conn.commit()
    conn.close()