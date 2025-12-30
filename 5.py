from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

from openai import OpenAI

openai = OpenAI()

question_1 = "Pick a buisiness area that might be worth exploring for an Agentic AI opportunity"

messages = [{"role":"user","content":question_1}]

response = openai.chat.completions.create(
    model = "gpt-4o-mini",
    messages= messages
)

buisiness_area = response.choices[0].message.content

question_2 = (f"What are the top 3 companies in the {buisiness_area} industry?" + "\n" + "Describe one major operational pain point in this industry that would be benifit from Agentic AI solutions")

print(question_2)

messages = [{"role":"user","content":question_2}]

response = openai.chat.completions.create(
    model = "gpt-4o-mini",
    messages= messages
)

pain_point = response.choices[0].message.content

question_3 = (f"How would an Agentic AI solution address the {pain_point} pain point?" + "\n" +  "Please propose a detailed plan for the Agentic AI solution")

print(question_3)

messages = [{"role":"user","content":question_3}]

response = openai.chat.completions.create(
    model = "gpt-4o-mini",
    messages= messages
)

answer  = response.choices[0].message.content

print(answer)

