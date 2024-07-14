from flask import Flask, render_template, jsonify, request, send_from_directory
from database import load_job_listings, mark_job_listing_inactive, get_job_listing_stats, save_job_listings, get_last_run_time, update_last_run_time, initialize_database
from filter_jobs import filter_jobs
from scraper import IndeedJobScraper

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/initialize_database', methods=['POST'])
def initialize_database_route():
    initialize_database()
    return jsonify({"message": "Database initialized successfully"})

@app.route('/job_listings')
def get_job_listings():
    status = request.args.get('status', 'ready')
    job_listings = load_job_listings(status)
    return jsonify(job_listings)

@app.route('/latest_job_listing')
def get_latest_job_listing():
    job_listing = load_job_listings(status='ready')
    if job_listing:
        return jsonify(job_listing[0])
    else:
        return jsonify(None)

@app.route('/mark_job_listing_inactive', methods=['POST'])
def mark_job_listing_inactive_route():
    job_id = request.json['job_id']
    mark_job_listing_inactive(job_id)
    return jsonify({"message": "Job listing marked as inactive successfully"})

@app.route('/job_listing_stats')
def get_job_listing_stats_route():
    stats = get_job_listing_stats()
    return jsonify(stats)

@app.route('/remove_job_listing', methods=['POST'])
def remove_job_listing_route():
    job_id = request.json['job_id']
    mark_job_listing_inactive(job_id)
    return jsonify({"message": "Job listing marked as inactive successfully"})

# @app.route('/run_filters', methods=['POST'])
# def run_filters_route():
#     filter_jobs()
#     return jsonify({"message": "Filters run successfully"})

@app.route('/scrape_jobs', methods=['POST'])
def scrape_jobs_route():
    num_jobs = int(request.form['num_jobs'])
    print(f'Attempting to scrape {num_jobs} jobs')
    job_scraper = IndeedJobScraper()
    job_listings = job_scraper.scrape_job_listings(num_jobs=num_jobs)
    save_job_listings(job_listings)
    return jsonify({"message": "Jobs scraped successfully"})

if __name__ == '__main__':
    app.run(debug=True)