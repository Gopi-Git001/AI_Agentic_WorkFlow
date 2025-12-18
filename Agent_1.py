from dotenv import load_dotenv

print(load_dotenv())

from google import genai

gemini = genai.Client()

models = gemini.models.list()

for i in models:
    print(i.name)