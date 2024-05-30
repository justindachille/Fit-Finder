import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from tqdm import tqdm
from database import initialize_database, save_job_listings, load_job_listings

torch.random.manual_seed(0)

def load_model():
    torch.random.manual_seed(0)
    model = AutoModelForCausalLM.from_pretrained(
        "microsoft/Phi-3-mini-128k-instruct",
        device_map="cuda",
        torch_dtype="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-128k-instruct")
    return model, tokenizer

def filter_sponsorship(job_listings):
    model, tokenizer = load_model()

    for job in tqdm(job_listings):
        if not job['sponsorship_checked']:
            prompt = f"Job Title: {job['title']}\nCompany: {job['company']}\nLocation: {job['location']}\nDescription: {job['description']}\n\nDoes this job offer sponsorship or not mention sponsorship? Answer YES if the job offers sponsorship or doesn't mention sponsorship. Answer NO if the job explicitly states that sponsorship is not offered or they are only hiring candidates who are already legally allowed to work in the country."

            messages = [{"role": "user", "content": prompt}]
            pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
            generation_args = {
                "max_new_tokens": 3,
                "return_full_text": False,
                "temperature": 0.0,
                "do_sample": False,
            }
            output = pipe(messages, **generation_args)
            answer = output[0]['generated_text'].strip()

            if answer.lower() == "no":
                job_listings.remove(job)
            else:
                job['sponsorship_checked'] = True

    save_job_listings(job_listings)

def main():
    initialize_database()
    job_listings = load_job_listings('sponsorship')
    filter_sponsorship(job_listings)

if __name__ == '__main__':
    main()