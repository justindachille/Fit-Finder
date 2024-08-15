# Indeed-Scraping

### Customization
* Add custom Indeed links into `base_urls` for jobs in file `scraper.py`

* Customize LLM prompts in `filter_jobs.py`

### Setup Instructions

* Authenticate Huggingface-cli with `huggingface-cli login --token [your token]`

* Start local app with `python app.py`

* Load `http://127.0.0.1:5000/` in browser

Notes:
LLM will be stored in ./llm_cache/ directory
