from  dotenv import load_dotenv

load_dotenv()

from google import genai

gemini = genai.Client()

model = gemini.models.list()

for model in model:
     print(model.name)

while True:

    question = input('You: ')

    if question in {'exit', 'quit'}:
        print('Thank you')
        break

    response = gemini.models.generate_content(
        model = "gemini-2.5-flash",
        contents = "question"
    )

    print("Gemini:", response.text)