import os

from dotenv import load_dotenv

#from scrapper import fetch_website_contents

from IPython.display import Markdown,display

from openai import OpenAI

import requests
from bs4 import BeautifulSoup

#print ("Hello world ")


load_dotenv(override=True)

# api_key = os.getenv('OPENAI_API_KEY')

# if api_key:
#     print("API KEY ")
# else:
#     print("not found")
    
    
# message = "Hey There!"

# messages =[ {'role':'user','content':message}]
    

# openai = OpenAI(api_key=api_key)


# response = openai.chat.completions.create(model='gpt-4o-mini',messages=messages)

# #print(response.choices[0].message.content)

# # models = openai.models.list()

# # for i in models:
# #     print(i)


# ed = requests.get("https://edwarddonner.com")
# print(BeautifulSoup(ed.text, "html.parser").get_text(" ", strip=True))



# # from markdownify import markdownify as md
# # markdown_text = "\n".join(line for line in md(ed.text).splitlines() if line.strip())
# # print(markdown_text[:2000])



api_key = os.getenv('OPENAI_API_KEY')


# message = 'can you act like as a Hiring Manager'

# messages = [{'role':'user','content':message}]

client = OpenAI()

# # for m in client.models.list():
# #     print(m)
    
# response = client.chat.completions.create(
#     model = 'gpt-4.1-mini',
#     messages = messages
# )

# print(response.choices[0].message.content)



system_prompt = """
You are a snarky assistant that analyzes the contents of a website,
and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""


user_prompt =  """
Here are the contents of a website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these too.
"""


def messages_for(website):
    
    return [{'role':'system','content':system_prompt},
            {'role':'user','content':user_prompt+website}]
    
    
def summarize(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()  # helpful: throws a clear error if request fails

    website = r.text   
    response = client.chat.completions.create(
        model = 'gpt-4.1-mini',
        messages=messages_for(website)        
    )
    
    return response.choices[0].message.content


print(summarize("https://edwarddonner.com"))

