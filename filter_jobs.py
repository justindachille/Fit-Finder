from tqdm import tqdm
from database import initialize_database, load_all_job_listings_filtered, mark_job_listing_inactive, update_job_listing_checked
from utils import load_model

def generate_response(model, tokenizer, messages, max_new_tokens=3):
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    )
    input_ids = inputs.to(model.device)

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    outputs = model.generate(
        input_ids,
        max_new_tokens=max_new_tokens,
        eos_token_id=terminators,
        do_sample=False,
        temperature=0.0,
        top_p=1.0,
        num_beams=1,
    )
    response = outputs[0][inputs.shape[-1]:]
    return tokenizer.decode(response, skip_special_tokens=True)

def filter_jobs():
    job_listings = load_all_job_listings_filtered('all')
    print(f'Total job listings: {len(job_listings)}')

    model, tokenizer = load_model()

    for job in tqdm(job_listings):
        if not job['sponsorship_checked']:
            print('Checking sponsorship for job:', job['title'])
            prompt = f"Job Title: {job['title']}\nCompany: {job['company']}\nLocation: \
                {job['location']}\nDescription: {job['description']}\n\nDoes this job offer sponsorship? \
                    Answer in one word: YES if the listing says the job offers sponsorship. \
                    Answer NO if the job explicitly \
                    states that sponsorship is not offered or they are only hiring candidates who are already \
                    legally allowed to work in the country. Remember to answer in one word: yes or no."
            messages = [{"role": "user", "content": prompt}]
            answer = generate_response(model, tokenizer, messages)
            print(f'Sponsorship answer: {answer}')
            if answer.lower() == "no":
                mark_job_listing_inactive(job['id'])
            else:
                job['sponsorship_checked'] = True
                update_job_listing_checked(job['id'], 'sponsorship')

        if job['sponsorship_checked'] and not job['candidate_fit_checked']:
            print('Checking candidate fit for job:', job['title'])
            prompt = f"Job Title: {job['title']}\nCompany: {job['company']}\nLocation: \
                {job['location']}\nDescription: {job['description']}\n\nCandidate Summary: \
                    The candidate is a recent graduate with a Master's degree in Computer Science, \
                    specializing in Machine Learning. They have experience as a Full Stack Software \
                    Engineer Intern, working with Python, Django, TypeScript, and React, as well as a \
                    Frontend Software Engineer Intern, working with React Native, TypeScript, Node, and \
                    REST APIs. The candidate has also conducted research in Federated Learning, implementing \
                    machine learning algorithms across GPU clusters, and has worked on projects involving \
                    Multivariate Time Series Transformers, Autonomous Vehicle Security, Web Application \
                    Development, Optimization Algorithms, and 3D Object Scanning.\n\nConsidering the job \
                    description and the candidate's background as a recent graduate with a Master's degree \
                    in Computer Science, is this role potentially suitable for the candidate? The ideal role \
                    should not require extensive experience, such as a lead developer position. Answer \
                    in one word: YES if the role aligns with the candidate's skills and the role \
                    does not require extensive experience. Answer NO if the role is clearly misaligned \
                    with the candidate's background or the role requires significant experience that \
                    the candidate likely does not possess as a recent graduate. Remember to answer \
                    in one word: yes or no."
            messages = [{"role": "user", "content": prompt}]
            answer = generate_response(model, tokenizer, messages)
            print(f'Candidate fit answer: {answer}')
            if answer.lower() == "no":
                mark_job_listing_inactive(job['id'])
            else:
                job['candidate_fit_checked'] = True
                update_job_listing_checked(job['id'], 'candidate_fit')

def main():
    initialize_database()
    filter_jobs()

if __name__ == '__main__':
    main()