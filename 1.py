from dotenv import load_dotenv
load_dotenv()

from google import genai

client = genai.Client()

print("Gemini CLI (type 'exit' to quit)\n")

while True:
    question = input("You: ").strip()    
    if question.lower() in {"exit", "quit"}:
        print("Goodbye!")
        break
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question
    )
    print("Gemini:", response.text, "\n")
