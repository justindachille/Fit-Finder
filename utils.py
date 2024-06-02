import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
torch.random.manual_seed(0)

def load_model():
    torch.random.manual_seed(0)
    model = AutoModelForCausalLM.from_pretrained(
        "microsoft/Phi-3-mini-128k-instruct",
        device_map="cuda",
        torch_dtype="auto",
        trust_remote_code=True,
        cache_dir="./llm_cache/",
    )
    tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-128k-instruct")
    return model, tokenizer