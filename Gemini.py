from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

google = genai.Client(api_key =os.getenv("GEMINI_API_KEY"))

model = "gemini-2.5-flash"

response = google.models.generate_content(
    model = model,
    contents = "Hello Gemini 2.5 Flash, how are you?"
)

print(response.text)
