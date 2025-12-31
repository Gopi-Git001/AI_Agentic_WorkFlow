from dotenv import load_dotenv
import os
load_dotenv()

from openai import OpenAI
from anthropic import Anthropic
from google import genai
from groq import Groq
# from deepseek import Deepseek


OpenAI_api_key = os.getenv("OPENAI_API_KEY")
Anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
Google_api_key = os.getenv("GOOGLE_API_KEY")
Groq_api_key = os.getenv("GROQ_API_KEY")
Deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")


if OpenAI_api_key:
    print("OpenAI API key is set")
else:
    print("OpenAI API key is not set")

if Anthropic_api_key:
    print("Anthropic API key is set")
else:
    print("Anthropic API key is not set")

if Google_api_key:
    print("Google API key is set")
else:
    print("Google API key is not set")

if Groq_api_key:
    print("Groq API key is set")
else:
    print("Groq API key is not set")

if Deepseek_api_key:
    print("Deepseek API key is set")
else:
    print("Deepseek API key is not set")
       
    
request = "please come up with a challenging,naunced question that I can ask a number of LLMs to evaluate their intelligence."

request  += "Answer only with the question,no explanation"

messages = [{'role':'user','content':request }]

openai = OpenAI()
