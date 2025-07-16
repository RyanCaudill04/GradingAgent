from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "deepseek-ai/deepseek-coder-6.7b-instruct"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Load model
model = AutoModelForCausalLM.from_pretrained(model_id)