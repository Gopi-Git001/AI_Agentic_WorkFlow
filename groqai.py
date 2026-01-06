# from dotenv import load_dotenv
# import os
# from openai import OpenAI

# load_dotenv()

# groq = OpenAI(api_key = os.getenv("GROQ_API_KEY"),base_url = "https://api.groq.com/openai/v1")

# message ='Hello Groq, how are you?'

# response = groq.responses.create(
#     model = "Llama-3.1-8b-instant",
#     input = message
# )

# print(response.output_text)


from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()

groq = OpenAI(api_key = os.getenv("GROQ_API_KEY"),base_url = "https://api.groq.com/openai/v1")

response = groq.chat.completions.create(
    model = "Llama-3.1-8b-instant",
    messages = [{"role":'user', 'content':"Hello Groq, how are you?"}]
)

print(response.choices[0].message.content)