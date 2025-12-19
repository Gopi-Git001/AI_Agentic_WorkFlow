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

response = gemini.models.generate_content(
    model = "gemini-2.5-flash",
    contents = "Could you please explain AI")

print(response.text)

print([x for x in dir(gemini) if not x.startswith("_")])
print([x for x in dir(gemini.models) if not x.startswith("_")])


# model = genai.GenerativeModel("gemini.2.5.flash")

# response = model.generate_content("Could you please explain AI")

# print(response.text)