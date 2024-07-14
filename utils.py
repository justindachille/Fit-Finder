import random
from time import sleep
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_model():
    model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token_id = tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        cache_dir="./llm_cache/",
    )
    return model, tokenizer

def stacked_random_wait():
    if random.random() > 0.8:
        sleep(random.uniform(10, 20))
    elif random.random() > 0.6:
        sleep(random.uniform(5, 10))
    elif random.random() > 0.4:
        sleep(random.uniform(2, 5))
    elif random.random() > 0.2:
        sleep(random.uniform(1, 2))
    else:
        sleep(random.uniform(0, 1))