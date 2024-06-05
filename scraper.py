from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from time import sleep
from random import uniform
import feedparser
from database import save_job_listings, get_job_listing_stats, load_job_listings

class IndeedJobScraper:
    def scrape_job_listings(self, num_jobs, max_retries=3):
        base_urls = [
            "https://uk.indeed.com/rss?q=computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/rss?q=software+engineer&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/rss?q=fullstack+developer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/rss?q=machine+learning+engineer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/rss?q=data+scientist+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/rss?q=devops+engineer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/rss?q=cloud+engineer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/rss?q=mobile+app+developer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/rss?q=embedded+systems+engineer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/rss?q=computer+vision+engineer+computer+science&l=London%2C+Greater+London&sort=date"
        ]
        start = 0
        job_listings = []
        print('count:', get_job_listing_stats()['total_count'], 'num jobs', num_jobs)
        while get_job_listing_stats()['total_count'] < num_jobs:
            print('Current jobs:', get_job_listing_stats()['total_count'], f'Scraping until {num_jobs} jobs')
            for base_url in base_urls:
                url = base_url + f"&start={start}"
                feed = feedparser.parse(url)
                print(f'Number of entries: {len(feed.entries)}')
                for i, entry in enumerate(feed.entries):
                    print(f'Scraping job: {i+1} of {len(feed.entries)}')
                    job_link = entry.link
                    job_id = job_link.split("jk=")[1].split("&")[0]
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
                    print(f'job id: {job_id}')
                    retries = 0
                    while retries < max_retries:
                        try:
                            with SB() as sb:
                                sb.open(job['link'])
                                job_description_div = WebDriverWait(sb.driver, 10).until(
                                    EC.presence_of_element_located((
                                        By.CSS_SELECTOR,
                                        '#jobDescriptionText, .jobsearch-jobDescriptionText, .jobDescription, .jobsearch-JobComponent-description'
                                    ))
                                )
                                job['description'] = job_description_div.text
                            break
                        except Exception as e:
                            print(f"Error occurred while scraping job description. Retrying... (Attempt {retries + 1}/{max_retries})")
                            retries += 1
                            if retries == max_retries:
                                print("Max retries reached. Skipping job listing.")
                                continue  # Skip job listings that consistently fail
                    job_listings.append(job)
                    save_job_listings([job])  # Save each job listing individually
                    if get_job_listing_stats()['total_count'] >= num_jobs:
                        print(f'Found enough jobs:', get_job_listing_stats()['total_count'])
                        return job_listings
                    sleep(uniform(1, 1.5))
                sleep(uniform(1, 1.5))
            start += 20
            sleep(uniform(1, 5))
        return job_listings