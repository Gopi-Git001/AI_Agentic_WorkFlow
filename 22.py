import os 
#import requests
from dotenv import load_dotenv
load_dotenv(override=True)
from openai import OpenAI
#api_key = os.getenv("OPENAI_API_KEY")


# if api_key :
#     print("API KEY FOUND")    
# else:
#     print("API NOT FOUND")


# headers = {'Authorization':f"Bearer {api_key}",'content_type':"application/json"}

# payload = {
#     'model' : "gpt-4.1-mini",
#     'messages':[
#         {'role':'user','content':
#             "tell me a Joke"}
#     ]
    
# }

# response = requests.post(
#     "https://api.openai.com/v1/chat/completions",
#     headers = headers,
#     json = payload
# )

# print(response.json()['choices'][0]['message']['content'])

message= [{'role':'user','content':'give me India capital'}]

def get_client(provider: str) -> OpenAI:
    base_url = os.getenv(f"{provider}_BASE_URL")
    api_key  = os.getenv(f"{provider}_API_KEY")
    if not base_url or not api_key:
        raise ValueError(f"Missing {provider}_BASE_URL or {provider}_API_KEY in .env")
    return OpenAI(base_url=base_url, api_key=api_key)

client  = get_client("OPENAI")

responce = client.chat.completions.create(
    model = 'gpt-4.1-mini',
    messages= message
    
)

print(responce.choices[0].message.content)
