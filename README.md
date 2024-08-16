# Indeed-Scraping

A Flask-based web application for efficient job listing management, leveraging the Meta-Llama-3-8B-Instruct model for intelligent filtering and analysis.

## Features

- Automated scraping of Indeed job listings based on customizable search queries
- Intelligent filtering using the Meta-Llama-3-8B-Instruct model to evaluate job listings for user defined parameters such as candidate fit
- SQLite database integration for efficient storage and retrieval of job data
- Web interface for easy visualization and interaction with scraped job listings
- On-demand manual scraping functionality through the user interface

## Customization (Do this before using)
* Add custom Indeed links into `base_urls` for jobs in file `scraper.py`
* Customize LLM prompts in `filter_jobs.py`

## Setup Instructions

- Clone the repository
- Install the required dependencies `pip install -r requirements.txt`
- Authenticate Huggingface-cli with `huggingface-cli login --token [your token]`
- Start local app with `python app.py`
- Load `http://127.0.0.1:5000/` in browser
- LLM will be automatically be stored in ./llm_cache/ directory

## To-do

* Button to restore the job that was least recently made inactive

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
