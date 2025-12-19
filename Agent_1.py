from dotenv import load_dotenv

print(load_dotenv())

from google import genai


import os   

google_api_key = os.getenv("GEMINI_API_KEY")

if google_api_key:
    print("Google API key is set")
else:
    print("Google API key is not set")

gemini = genai.Client()

models = gemini.models.list()

# for i in models:
#     print(i.name)    


import os
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
print("Found .env at:", dotenv_path)

loaded = load_dotenv(dotenv_path)
print("load_dotenv returned:", loaded)

print("CWD:", os.getcwd())
print("GOOGLE_API_KEY value:", repr(os.getenv("GOOGLE_API_KEY")))
print("All env keys containing 'KEY':", [k for k in os.environ.keys() if "KEY" in k])

