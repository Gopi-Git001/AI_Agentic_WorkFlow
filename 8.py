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
model_name = "llama-3.1-8b-instant"
response = groq.chat.completions.create(
    model = model_name,
    messages = messages
)
answer = response.choices[0].message.content
print(f"Groq: {answer}")
competitors.append(model_name)
answers.append(answer)

for competitor, answer in zip(competitors, answers):
    print(f"{competitor}: {answer}")

together = ''
for competitor, answer in zip(competitors, answers):
    together += f"{competitor}: {answer}\n\n"
    together+=answer+"\n\n"

print(together)

judge = f"""You are judging a competition between {len(competitors)} competitors.
Each model has been given this question:

{question}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
Respond with JSON, and only JSON, with the following format:
{{"results": ["best competitor number", "second best competitor number", "third best competitor number", ...]}}

Here are the responses from each competitor:

{together}

Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks."""



judge_messages =[{'role':'user','content':judge}]
response = openai.chat.completions.create(
    model = "gpt-5-mini",
    messages = judge_messages,
)

results = response.choices[0].message.content.strip()



import json
results_dict = json.loads(results)
ranks = results_dict["results"]
for index, result in enumerate(ranks):
    competitor = competitors[int(result)-1]
    print(f"Rank {index+1}: {competitor}")


