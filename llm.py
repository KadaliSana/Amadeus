from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from stt import stt
import torch
from huggingface_hub import login

login(token="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")
# Use the quantized or full model path from Hugging Face
MODEL_NAME = "google/gemma-3-4b-it-qat-q4_0-gguf"

# Check GPU availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
model.to(device)

# Define the prompt
prompt = stt.listen()

# Tokenize and generate
inputs = tokenizer(prompt, return_tensors="pt").to(device)
outputs = model.generate(**inputs, max_new_tokens=200, do_sample=True, temperature=0.7)

# Decode and print result
result = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("Response:\n", result)
