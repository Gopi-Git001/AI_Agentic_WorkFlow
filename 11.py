from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import OpenAI

openai = OpenAI()
# message = {"role":"user","content":"what is Gravity?"}
question = "Please propose a hard, challenging question to assess someone's IQ. Respond only with the question."
message = [{"role":"user","content":question}]

response = openai.chat.completions.create(
    model = "gpt-4o-mini",
    messages= message
)

question = response.choices[0].message.content

print(question)

messages = [{"role":"user","content":question}]

response = openai.chat.completions.create(
    model = "gpt-4o-mini",
    messages= messages
)

answer = response.choices[0].message.content

print(answer)
