import sqlite3
from datetime import datetime

def initialize_database():
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS job_listings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT,
                 company TEXT,
                 location TEXT,
                 published TEXT,
                 salary TEXT,
                 summary TEXT,
                 link TEXT,
                 description TEXT,
                 sponsorship_checked INTEGER,
                 candidate_fit_checked INTEGER)''')

    c.execute('''CREATE TABLE IF NOT EXISTS run_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 run_time TEXT)''')

    conn.commit()
    conn.close()

def save_job_listings(job_listings):
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    for job in job_listings:
        c.execute("INSERT INTO job_listings (title, company, location, published, salary, summary, link, description, sponsorship_checked, candidate_fit_checked) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (job['title'], job['company'], job['location'], job['published'], job['salary'], job['summary'], job['link'], job['description'], job['sponsorship_checked'], job['candidate_fit_checked']))

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

def update_last_run_time(last_published_time):
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    c.execute("INSERT INTO run_history (run_time) VALUES (?)", (last_published_time,))

    conn.commit()
    conn.close()

def load_job_listings(filter_type):
    conn = sqlite3.connect('job_listings.db')
    c = conn.cursor()

    if filter_type == 'sponsorship':
        c.execute("SELECT * FROM job_listings WHERE sponsorship_checked = 0")
    elif filter_type == 'candidate_fit':
        c.execute("SELECT * FROM job_listings WHERE candidate_fit_checked = 0")
    else:
        raise ValueError("Invalid filter type. Must be 'sponsorship' or 'candidate_fit'.")

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
            'candidate_fit_checked': bool(row[10])
        }
        job_listings.append(job)

    conn.close()

    return job_listings