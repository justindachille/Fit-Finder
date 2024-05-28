import feedparser
from seleniumbase import BaseCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

class IndeedJobScraper(BaseCase):
    def scrape_job_description(self, url):
        self.open(url)
        try:
            job_description_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    '#jobDescriptionText, .jobsearch-jobDescriptionText, .jobDescription, .jobsearch-JobComponent-description'
                ))
            )
            job_description = job_description_div.text
            return job_description
        except Exception as e:
            print("Job description not found.", e)
            return None

if __name__ == '__main__':
    url = "https://uk.indeed.com/rss?q=software+engineer&l=london&sort=date&fromage=1&vjk=a8d02a4d0d5ba596"
    feed = feedparser.parse(url)
    job_listings = []

    scraper = IndeedJobScraper()
    scraper.setUp()

    for entry in feed.entries:
        job = {
            'title': entry.title,
            'company': entry.source.title,
            'location': entry.get('location', 'London'),
            'published': entry.published,
            'salary': None,
            'summary': entry.summary,
            'link': entry.link,
            'description': scraper.scrape_job_description(entry.link)
        }
        job_listings.append(job)

    scraper.tearDown()

    for job in job_listings:
        print(job)

    # Pickle the job listings
    with open('job_listings.pkl', 'wb') as file:
        pickle.dump(job_listings, file)