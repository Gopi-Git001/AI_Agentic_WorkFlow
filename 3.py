from  dotenv import load_dotenv

load_dotenv()

from google import genai

gemini = genai.Client()

model = gemini.models.list()

for model in model:
    print(model.name)
