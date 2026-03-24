import os

def check_key(name):
    key = os.getenv(name)
    if key:
        print(f"{name} is set: {key[:4]}...{key[-4:]} (length: {len(key)})")
    else:
        print(f"{name} is NOT set")

print("--- Environment Check ---")
check_key("OPENAI_API_KEY")
check_key("GROQ_API_KEY")
check_key("LLM_PROVIDER")
print("-------------------------")
