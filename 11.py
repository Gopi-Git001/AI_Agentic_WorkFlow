from dotenv import load_dotenv
import os


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("exist")

else:
    print("Nothing")
