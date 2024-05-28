import feedparser
from seleniumbase import BaseCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

BaseCase.main(__name__, __file__)

class IndeedJobScraper(BaseCase):
    def test_scrape_job_listings(self):
        url = "https://uk.indeed.com/rss?q=software+engineer&l=london&sort=date&fromage=1&vjk=a8d02a4d0d5ba596"
        feed = feedparser.parse(url)
        job_listings = []

        for entry in feed.entries:
            job = {
                'title': entry.title,
                'company': entry.source.title,
                'location': entry.get('location', 'London'),
                'published': entry.published,
                'salary': None,
                'summary': entry.summary,
                'link': entry.link,
                'description': None
            }

            # Scrape the job description
            self.open(entry.link)
            try:
                job_description_div = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        '#jobDescriptionText, .jobsearch-jobDescriptionText, .jobDescription, .jobsearch-JobComponent-description'
                    ))
                )
                job['description'] = job_description_div.text
                print(f"Description: {job['description']}")
            except Exception as e:
                print("Job description not found.", e)

            job_listings.append(job)

        for job in job_listings:
            print(job)

        # Pickle the job listings
        with open('job_listings.pkl', 'wb') as file:
            pickle.dump(job_listings, file)
