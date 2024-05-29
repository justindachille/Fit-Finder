import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import pickle
from PyPDF2 import PdfReader
from tqdm import tqdm

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

def read_resume(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        resume = ""
        for page in pdf_reader.pages:
            resume += page.extract_text()
    return resume

def filter_job_listings(job_listings, resume):
    model, tokenizer = load_model()
    filtered_listings = []

    for job in tqdm(job_listings):
        prompt = f"Job Title: {job['title']}\nCompany: {job['company']}\nLocation: {job['location']}\nDescription: {job['description']}\n\nCandidate Summary: The candidate is a recent graduate with a Master's degree in Computer Science, specializing in Machine Learning. They have experience as a Full Stack Software Engineer Intern, working with Python, Django, TypeScript, and React, as well as a Frontend Software Engineer Intern, working with React Native, TypeScript, Node, and REST APIs. The candidate has also conducted research in Federated Learning, implementing machine learning algorithms across GPU clusters, and has worked on projects involving Multivariate Time Series Transformers, Autonomous Vehicle Security, Web Application Development, Optimization Algorithms, and 3D Object Scanning.\n\nConsidering the job description and the candidate's background as a recent graduate with a Master's degree in Computer Science, is this role potentially suitable for the candidate? The ideal role should not require extensive experience, such as a lead developer position. Additionally, does the job offer sponsorship, not mention sponsorship, or not explicitly state that sponsorship is unavailable? Answer YES if the role aligns with the candidate's skills and either offers sponsorship, doesn't mention sponsorship, or doesn't explicitly state that sponsorship is unavailable, and the role does not require extensive experience. Answer NO if the role is clearly misaligned with the candidate's background, explicitly states that sponsorship is not offered, they are only hiring candidates who are already legally allowed to work in the country, or the role requires significant experience that the candidate likely does not possess as a recent graduate."
        # print(f'prompt: {prompt}')
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
        
        if answer.lower() == "yes":
            filtered_listings.append(job)
        # print(f'answer: {answer}')
        # break
    return filtered_listings

def main():
    with open('job_listings.pkl', 'rb') as file:
        job_listings = pickle.load(file)
    
    resume_file_path = 'resume.pdf'
    resume = read_resume(resume_file_path)
    
    filtered_listings = filter_job_listings(job_listings, resume)
    
    with open('filtered_job_listings.pkl', 'wb') as file:
        pickle.dump(filtered_listings, file)

if __name__ == '__main__':
    main()