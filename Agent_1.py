import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Client auto-reads GEMINI_API_KEY
client = genai.Client()

MODEL = "gemini-2.5-flash"  # change if needed

history = []

def send_message(text):
    global history

    history.append({
        "role": "user",
        "parts": [{"text": text}]
    })

    response = client.models.generate_content(
        model=MODEL,
        contents=history
    )

    history.append({
        "role": "model",
        "parts": [{"text": response.text}]
    })

    return response.text


print(send_message("Hi!"))
print(send_message("What is the capital of France?"))
