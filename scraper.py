from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from time import sleep
from random import uniform
import feedparser
from database import save_job_listings, get_last_run_time, update_last_run_time, get_job_listing_stats, load_job_listings

class IndeedJobScraper:
    def scrape_job_listings(self, last_run_time, num_jobs):
        base_url = "https://uk.indeed.com/rss?q=software+engineer&l=london&sort=date&fromage=1&vjk=a8d02a4d0d5ba596"
        start = 0
        job_listings = []
        while get_job_listing_stats()['total_count'] < num_jobs:
            print('Current jobs:', get_job_listing_stats()['total_count'], f'Scraping until {num_jobs} jobs')
            url = base_url + f"&start={start}"
            feed = feedparser.parse(url)
            print(f'Number of entries: {len(feed.entries)}')

            for i, entry in enumerate(feed.entries):
                print(f'Scraping job: {i+1} of {len(feed.entries)}')
                job_id = entry.link.split("jk=")[-1]
                existing_job = load_job_listings(job_id=job_id)
                if existing_job:
                    print(f"Skipping duplicate job: {job_id}")
                    continue  # Skip duplicate job listings
                job = {
                    'id': job_id,
                    'title': entry.title,
                    'company': entry.source.title,
                    'location': entry.location if 'location' in entry else 'London',
                    'published': entry.published,
                    'salary': None,
                    'summary': entry.summary,
                    'link': entry.link,
                    'description': None,
                    'sponsorship_checked': False,
                    'candidate_fit_checked': False,
                    'inactive': False,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                # Scrape the job description
                print('Link:', job['link'])
                with SB() as sb:
                    try:
                        sb.open(job['link'])
                        job_description_div = WebDriverWait(sb.driver, 10).until(
                            EC.presence_of_element_located((
                                By.CSS_SELECTOR,
                                '#jobDescriptionText, .jobsearch-jobDescriptionText, .jobDescription, .jobsearch-JobComponent-description'
                            ))
                        )
                        job['description'] = job_description_div.text
                    except Exception as e:
                        print("Job description not found.", e)
                        continue  # Skip job listings without a description
                job_listings.append(job)
                save_job_listings([job])  # Save each job listing individually
                if get_job_listing_stats()['total_count'] >= num_jobs:
                    print(f'Found enough jobs:', get_job_listing_stats()['total_count'])
                    update_last_run_time(job['published'])
                    return job_listings
                sleep(uniform(1, 1.5))
            start += 20
            sleep(uniform(1, 5))
        update_last_run_time(job_listings[-1]['published'] if job_listings else None)
        return job_listings