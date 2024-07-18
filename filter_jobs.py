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
                {job['location']}\nDescription: {job['description']}\n\nDoes this job offer UK work visa sponsorship? \
                Answer YES only if the listing specifically mentions offering UK work visa sponsorship, \
                or if it's a relatively big and/or international company (which typically can sponsor work visas). \
                Answer NO if the job explicitly states that sponsorship is not offered or they are only hiring candidates \
                who are already legally allowed to work in the country. Remember to answer in one word: yes or no."
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
                Recent graduate with a Master's in Computer Science, specializing in Machine Learning. \
                Has internship experience in Full Stack and Frontend Software Engineering, and research \
                experience in Federated Learning.\n\nIs this role suitable for someone with a Master's \
                in Computer Science who is a recent graduate? Answer YES only if the role aligns well \
                with the candidate's skills and educational background, and does not require extensive \
                experience. Answer NO if the role is misaligned with the candidate's background or if \
                it's a staff, senior, or other high-level position that would not be suitable for a \
                recent graduate. Remember to answer in one word: yes or no."
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