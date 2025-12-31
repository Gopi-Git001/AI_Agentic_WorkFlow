from dotenv import load_dotenv
import os
load_dotenv()
from groq import Groq
from openai import OpenAI
from anthropic import Anthropic


request = "please come up with a challenging,naunced question that I can ask a number of LLMs to evaluate their intelligence."

request  += "Answer only with the question,no explanation"

messages = [{'role':'user','content':request }]

openai = OpenAI()

response = openai.chat.completions.create(
    model = "gpt-4o-mini",
    messages = messages
)

question = response.choices[0].message.content 


competitors = []
answers = []
model_name = "gpt-4o-mini"
messages = [{'role':'user','content':question  }]
response = openai.chat.completions.create(
    model = model_name,
    messages = messages
)

answer = response.choices[0].message.content 
print(f"{model_name}: {answer}")

competitors.append(model_name)
answers.append(answer)

claude = Anthropic()

model_name = "claude-sonnet-4-5"
messages = [{'role':'user','content':question  }]

response = claude.messages.create(
    model = model_name,messages = messages,max_tokens = 1000
)

answer = response.content[0].text
print(f"{model_name}: {answer}")
competitors.append(model_name)
answers.append(answer)


Groq_api_key = os.getenv("GROQ_API_KEY")
messages = [{'role':'user','content':question}]
groq = Groq(api_key=Groq_api_key)
response = groq.chat.completions.create(
    model = "llama-3.1-8b-instant",
    messages = messages
)
answer = response.choices[0].message.content
print(f"Groq: {answer}")
competitors.append(model_name)
answers.append(answer)

