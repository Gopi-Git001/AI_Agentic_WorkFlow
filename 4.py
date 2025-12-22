import os
from dotenv import load_dotenv, find_dotenv

env_path = find_dotenv()
print("dotenv path:", env_path)

load_dotenv(env_path, override=True)

key = os.getenv("GEMINI_API_KEY")
print("key loaded:", None if not key else (key[:6] + "..." + key[-4:]))
print("key length:", 0 if not key else len(key))


from dotenv import load_dotenv
load_dotenv(override=True)

from google import genai
client = genai.Client()

while True :
    question = input('You:')
    if question in  {"exit","quit"}:
        print("Thank you")
        break


    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question
    )
    print(resp.text)
