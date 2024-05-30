from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from time import sleep
from random import uniform
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode

class IndeedJobScraper:
    def scrape_job_listings(self, last_run_time, num_jobs):
        base_url = "https://uk.indeed.com/rss?q=software+engineer&l=london&sort=date&fromage=1&vjk=a8d02a4d0d5ba596"
        start = 0
        job_listings = []
        with SB() as sb:
            while len(job_listings) < num_jobs:
                url = base_url + f"&start={start}"
                print(f'url: {url}')
                sb.open(url)
                sleep(2)
                pre_element = sb.find_element(By.CSS_SELECTOR, 'pre')
                xml_content = pre_element.get_attribute('innerText')
                xml_content = xml_content.replace('&amp;', '&')
                print(f'xml content: {xml_content[:2000]}')
                soup = BeautifulSoup(xml_content, 'xml')
                items = soup.find_all('item')
                print(f'Number of items: {len(items)}')
                for item in items:
                    job_link = item.link.text
                    parsed_url = urlparse(job_link)
                    query_params = parse_qs(parsed_url.query)
                    query_params = {k: v[0] for k, v in query_params.items()}
                    job_id = query_params.get('jk')
                    if job_id in [job['id'] for job in job_listings]:
                        continue  # Skip duplicate job listings
                    job = {
                        'id': job_id,
                        'title': item.title.text,
                        'company': item.source.text,
                        'location': item.location.text if item.location else 'London',
                        'published': item.pubDate.text,
                        'salary': None,
                        'summary': item.description.text,
                        'link': job_link,
                        'description': None,
                        'sponsorship_checked': False,
                        'candidate_fit_checked': False
                    }
                    published_time = datetime.strptime(job['published'], "%a, %d %b %Y %H:%M:%S %Z")
                    if last_run_time and published_time <= last_run_time:
                        return job_listings
                    print('job link', job['link'])
                    assert False
                    # Scrape the job description
                    print('link', job['link'])
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
                    assert False
                    if len(job_listings) >= num_jobs:
                        return job_listings
                start += 20
                sleep(uniform(1, 3))
        return job_listings