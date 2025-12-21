from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

client = genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

while True:
    question = input('You:' )

    if question == 'exit' or question == 'quit':
        print('Thank you')
        break
    response = client.models.generate_content(

        model="gemini-2.5-flash",
        contents=question
    )
    print("Gemini:", response.text)
