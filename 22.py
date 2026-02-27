import os 
import requests
from dotenv import load_dotenv
load_dotenv(override=True)
from openai import OpenAI
api_key = os.getenv("OPENAI_API_KEY")

client  = OpenAI()

if api_key :
    print("API KEY FOUND")    
else:
    print("API NOT FOUND")

headers = {'Authorization':f"Bearer {api_key}",'content_type':"application/json"}

payload = {
    'model' : "gpt-4.1-mini",
    'messages':[
        {'role':'user','content':
            "tell me a Joke"}
    ]
    
}

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers = headers,
    json = payload
)

print(response.json()['choices'][0]['message']['content'])

message= [{'role':'user','content':'Tell me a joke'}]

responce = client.chat.completions.create(
    model = 'gpt-4.1-mini',
    messages= message
    
)


print(responce.choices[0].message.content)
