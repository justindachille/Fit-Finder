from database import initialize_database, save_job_listings, get_last_run_time, update_last_run_time, prune_old_job_listings
from scraper import IndeedJobScraper

def main():
    initialize_database()
    last_run_time = get_last_run_time()
    job_scraper = IndeedJobScraper()
    job_listings = job_scraper.scrape_job_listings(last_run_time, num_jobs=10)
    save_job_listings(job_listings)
    update_last_run_time(job_listings[-1]['published'])
    prune_old_job_listings()

if __name__ == '__main__':
    main()