from transformers import pipeline
from tqdm import tqdm
from database import initialize_database, load_all_job_listings_filtered, mark_job_listing_inactive, update_job_listing_checked
from utils import load_model

running_jobs = []

def filter_jobs():
    global running_jobs
    job_listings = load_all_job_listings_filtered('all')
    print(f'Total job listings: {len(job_listings)}')

    model, tokenizer = load_model()

    for job in tqdm(job_listings):
        if not job['sponsorship_checked']:
            running_jobs.append(job['title'])
            print('Checking sponsorship for job:', job['title'])
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
            print(f'Sponsorship answer: {answer}')
            if answer.lower() == "no":
                mark_job_listing_inactive(job['id'])
            else:
                job['sponsorship_checked'] = True
                update_job_listing_checked(job['id'], 'sponsorship')
            running_jobs.remove(job['title'])

        if job['sponsorship_checked'] and not job['candidate_fit_checked']:
            running_jobs.append(job['title'])
            print('Checking candidate fit for job:', job['title'])
            prompt = f"Job Title: {job['title']}\nCompany: {job['company']}\nLocation: {job['location']}\nDescription: {job['description']}\n\nCandidate Summary: The candidate is a recent graduate with a Master's degree in Computer Science, specializing in Machine Learning. They have experience as a Full Stack Software Engineer Intern, working with Python, Django, TypeScript, and React, as well as a Frontend Software Engineer Intern, working with React Native, TypeScript, Node, and REST APIs. The candidate has also conducted research in Federated Learning, implementing machine learning algorithms across GPU clusters, and has worked on projects involving Multivariate Time Series Transformers, Autonomous Vehicle Security, Web Application Development, Optimization Algorithms, and 3D Object Scanning.\n\nConsidering the job description and the candidate's background as a recent graduate with a Master's degree in Computer Science, is this role potentially suitable for the candidate? The ideal role should not require extensive experience, such as a lead developer position. Answer YES if the role aligns with the candidate's skills and the role does not require extensive experience. Answer NO if the role is clearly misaligned with the candidate's background or the role requires significant experience that the candidate likely does not possess as a recent graduate."
            messages = [{"role": "user", "content": prompt}]
            output = pipe(messages, **generation_args)
            answer = output[0]['generated_text'].strip()
            print(f'Candidate fit answer: {answer}')
            if answer.lower() == "no":
                mark_job_listing_inactive(job['id'])
            else:
                job['candidate_fit_checked'] = True
                update_job_listing_checked(job['id'], 'candidate_fit')
            running_jobs.remove(job['title'])

def main():
    initialize_database()
    filter_jobs()

if __name__ == '__main__':
    main()