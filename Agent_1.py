from dotenv import load_dotenv

print(load_dotenv())

from google import genai

gemini = genai.Client()

models = gemini.models.list()

# for i in models:
#     print(i.name)    
import os   

google_api_key = os.getenv("GOOGLE_API_KEY")

if google_api_key:
    print("Google API key is set")
else:
    print("Google API key is not set")