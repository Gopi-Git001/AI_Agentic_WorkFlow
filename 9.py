from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
import gradio as gr

load_dotenv()
openai = OpenAI()

reader = PdfReader("me/linkedin.pdf")
linkedin = ''
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

with  open("me/summary.txt","r",encoding="utf-8") as f:
    summary = f.read()

name = "Gopi Thungam"

system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer, say so."
system_prompt += f"\n\n## summary:\n{summary}\n\n##  LinkedIn profile:\n\n{linkedin}"
system_prompt += f" with this context,please chat with the user,always staying in character as {name}."


def chat(message,history):
    messages = [{"role":"system","content":system_prompt}]+history+[{"role":"user","content":message}]
    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages
    )
    return response.choices[0].message.content

gr.ChatInterface(chat).launch(share = True)
