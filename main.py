from transformers import pipeline

ia = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct")

prompt = ""

resposta = ia(prompt, max_new_tokens=300, temperature=0.3)
