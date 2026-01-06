from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

deepseek = OpenAI(api_key = os.getenv("DEEPSEEK_API_KEY"),base_url = "https://api.deepseek.com")

message = [{"role":'user', 'content':"Hello DeepSeek, how are you?"}]

response = deepseek.chat.completions.create(
    model = "deepseek-chat",
    messages = message
)

print(response.choices[0].message.content)