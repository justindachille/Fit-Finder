import csv
import random
from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from time import sleep
from random import uniform
from database import save_job_listings, get_job_listing_stats, load_job_listings

# Global flag to control proxy usage
USE_PROXY = False

class IndeedJobScraper:
    def __init__(self, proxy_file='./proxies/megaproxylist.csv'):
        self.proxy_file = proxy_file
        self.proxies = self.load_and_filter_proxies() if USE_PROXY else []

    def load_and_filter_proxies(self):
        proxies = []
        with open(self.proxy_file, 'r') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                reliability = float(row['RELIABILITY'].strip('%'))
                if reliability >= 95:
                    proxies.append({
                        'IP': row['IP'],
                        'PORT': row['PORT'],
                        'COUNTRY': row['COUNTRY'],
                        'RELIABILITY': row['RELIABILITY'],
                        'url': f"https://{row['IP']}:{row['PORT']}"
                    })
        return proxies

    def get_random_proxy(self):
        return random.choice(self.proxies) if self.proxies else None

    def scrape_job_listings(self, num_jobs, max_retries=3):
        base_urls = [
            "https://uk.indeed.com/jobs?q=computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/jobs?q=software+engineer&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/jobs?q=fullstack+developer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/jobs?q=machine+learning+engineer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/jobs?q=data+scientist+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/jobs?q=devops+engineer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/jobs?q=cloud+engineer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/jobs?q=mobile+app+developer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/jobs?q=embedded+systems+engineer+computer+science&l=London%2C+Greater+London&sort=date",
            "https://uk.indeed.com/jobs?q=computer+vision+engineer+computer+science&l=London%2C+Greater+London&sort=date"
        ]
        url_start_positions = {url: 0 for url in base_urls}  # Track start position for each URL
        job_listings = []
        print('count:', get_job_listing_stats()['total_count'], 'num jobs', num_jobs)
        zero_entry_count = 0

        while get_job_listing_stats()['total_count'] < num_jobs:
            print('Current jobs:', get_job_listing_stats()['total_count'], f'Scraping until {num_jobs} jobs')
            all_zero_entries = True
            for base_url in base_urls:
                start = url_start_positions[base_url]
                url = base_url + f"&start={start}"
                proxy = self.get_random_proxy() if USE_PROXY else None
                
                try:
                    with SB(uc=True, proxy=proxy['url'] if proxy else None) as sb:
                        sb.open(url)
                        
                        # Wait for the job cards to load
                        WebDriverWait(sb.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "td.resultContent"))
                        )
                        
                        # Find all job cards
                        job_cards = sb.find_elements("css selector", "td.resultContent")
                        num_cards = len(job_cards)
                        print(f'got job cards: {num_cards}')
                        
                        if num_cards > 0:
                            all_zero_entries = False
                        
                        print(f'Number of entries: {num_cards}')
                        
                        # First, extract all data from job cards
                        jobs_data = []
                        for i, card in enumerate(job_cards):
                            print(f'Extracting data from job card: {i+1} of {num_cards}')
                            try:
                                link_element = card.find_element(By.CSS_SELECTOR, "a[id^='job_']")
                                job_id = link_element.get_attribute('id').split('_')[1]
                                job_link = link_element.get_attribute('href')
                                if not job_link.startswith('https://'):
                                    job_link = f"https://uk.indeed.com{job_link}"
                                
                                job_title = link_element.find_element(By.CSS_SELECTOR, "span[id^='jobTitle-']").text
                                company = card.find_element(By.CSS_SELECTOR, "span[data-testid='company-name']").text
                                location = card.find_element(By.CSS_SELECTOR, "div[data-testid='text-location']").text
                                
                                jobs_data.append({
                                    'id': job_id,
                                    'title': job_title,
                                    'company': company,
                                    'location': location,
                                    'link': job_link,
                                })
                            except Exception as e:
                                print(f"Error extracting data from job card: {e}")
                        
                        # Now, fetch descriptions for each job
                        for job_data in jobs_data:
                            existing_job = load_job_listings(job_id=job_data['id'])
                            if existing_job:
                                print(f"Skipping duplicate job: {job_data['id']}")
                                continue  # Skip duplicate job listings
                            
                            job = {
                                'id': job_data['id'],
                                'title': job_data['title'],
                                'company': job_data['company'],
                                'location': job_data['location'],
                                'published': datetime.now().strftime("%Y-%m-%d"),
                                'salary': None,
                                'summary': None,
                                'link': job_data['link'],
                                'description': None,
                                'sponsorship_checked': False,
                                'candidate_fit_checked': False,
                                'inactive': False,
                                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            # Fetch job description
                            print('Fetching description for:', job['link'])
                            retries = 0
                            while retries < max_retries:
                                try:
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
                                        print("Max retries reached. Skipping job description.")
                                        job['description'] = None
                            
                            job_listings.append(job)
                            save_job_listings([job])
                            
                            if get_job_listing_stats()['total_count'] >= num_jobs:
                                print(f'Found enough jobs:', get_job_listing_stats()['total_count'])
                                return job_listings
                            
                            sleep(uniform(1, 1.5))
                        
                        # Update the start position for this URL
                        url_start_positions[base_url] += num_cards
                
                except Exception as e:
                    print(f"Error opening URL {url}: {e}")
                
                sleep(uniform(1, 1.5))
            
            if all_zero_entries:
                zero_entry_count += 1
                if zero_entry_count == 3:
                    print("Detected 0 entries for all links 3 times in a row. Stopping the scraper.")
                    return job_listings
            else:
                zero_entry_count = 0
            
            sleep(uniform(1, 5))
        
        return job_listings