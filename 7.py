from dotenv import load_dotenv
import os
load_dotenv()

from openai import OpenAI
from anthropic import Anthropic

OpenAI_api_key = os.getenv("OPENAI_API_KEY")
Anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
Google_api_key = os.getenv("GOOGLE_API_KEY")
Groq_api_key = os.getenv("GROQ_API_KEY")
Deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")


if OpenAI_api_key:
    print("OpenAI API key is set")
elif Anthropic_api_key:
    print("Anthropic API key is set")
elif Google_api_key:
    print("Google API key is set")
elif Groq_api_key:
    print("Groq API key is set")
elif Deepseek_api_key:
    print("Deepseek API key is set")
else:
    print("No API key is set")
