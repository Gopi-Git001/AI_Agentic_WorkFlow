from dotenv import load_dotenv
import os 
from openai import OpenAI

load_dotenv()

openai = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

message = [{"role":'user', 'content':"Hello OpenAI, how are you?"}]

response = openai.chat.completions.create(
    model = "gpt-4o-mini",
    messages = message
)
print(response.choices[0].message.content)
