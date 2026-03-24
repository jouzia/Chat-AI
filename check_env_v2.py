import os

def check_key(name):
    key = os.getenv(name, "")
    if key:
        print(f"{name}: starts with '{key[:3]}', length {len(key)}")
    else:
        print(f"{name}: NOT SET")

print("--- DIAGNOSTIC ---")
check_key("OPENAI_API_KEY")
check_key("GROQ_API_KEY")
check_key("LLM_PROVIDER")
check_key("OLLAMA_MODEL")
print("-----------------")
