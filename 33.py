import os
import json 
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from IPython.display import Markdown,display,update_display
from dotenv import load_dotenv
from web_scraper import fetch_website_links, fetch_website_contents
load_dotenv(override=True)


def get_client(provider:str) -> OpenAI:
    base_url = os.getenv(f"{provider}_BASE_URL")
    api_key = os.getenv(f"{provider}_API_KEY")
    if not base_url or not api_key:
        raise ValueError(f" Missing {provider} base_url or {provider} api_key")    
    return OpenAI(base_url=base_url,api_key=api_key)

links = requests.get("https://edwarddonner.com",timeout=20)


MODEL = 'gpt-5-nano'

client = get_client("OPENAI")

links_system_prompt = """
    You are provided with a list of links found on  webpage. 
    You are able to decide which of the links would be most relevant to include in a brochure about the company,
    such as links to an About PAge,or a Company page, or Careers/Jobs pages.
    You should respond in JSON as in this example:
    
    {
        "links":[
            {"type":"about page","url":"https://full.url/goes/here/about"}
            {"type":"careers page","url":"https://another.full.url/careers"}
        ]
    }

"""

def get_links_user_prompt(url):
    user_prompt = f"""
Here is the list of links on the website {url} -
Please decide which of these are relevant web links for a brochure about the company, 
respond with the full https URL in JSON format.
Do not include Terms of Service, Privacy, email links.

Links (some might be relative links):

"""
    links = fetch_website_links(url)
    user_prompt += "\n".join(links)
    return user_prompt


def select_relevant_links(url):  
    messages = [
    {'role':'system','content':links_system_prompt},
    {'role':'user','content':get_links_user_prompt(url)}
    ]  
    response = client.chat.completions.create(
        model = MODEL,
        messages=messages,
        response_format={"type":"json_object"}
    )
    
    result = response.choices[0].message.content 
    links = json.loads(result)
    return links

#print(select_relevant_links("https://edwarddonner.com"))

def fetch_page_and_all_relevant_links(url):
    contents = fetch_website_contents(url)
    relavant_links = select_relevant_links(url)
    output= []
    for link in relavant_links['links'][:5]:
        link_type = link['type']
        link_url = link['url']
        output.append(link_type)
        output.append(fetch_website_contents(link_url))
        try:
            output.append(fetch_website_contents(link_url))
        except requests.exceptions.HTTPError as e:
            output.append(f"[Skipped: {link_url} returned an error: {e}]")
        except requests.exceptions.RequestException as e:
            output.append(f"[Skipped: {link_url} request failed: {e}]")
        
    return "\n\n".join(output) 


brochure_system_prompt = """
You are a assistant that analyze the content of severl relevant pages from a company website
and creates a short brochure about the company for prospective customers ,investors and recruiters.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information .
"""

def get_brochure_user_prompt(company_name,url):
    
    user_prompt = """
    
    You are looking at a company called :{company_name}.
    Here are the contents of its landing page and other relevant pages ;
    use this information to build a short brochure of the company in markdown without code blocks .\n\n    
    """
    
    user_prompt += fetch_page_and_all_relevant_links(url)
    
    user_prompt = user_prompt[:5_000]
    
    return user_prompt


def create_brochure(company_name,url):
    response = client.chat.completions.create(
        model = MODEL,
        messages = [
            {
                'role':'system','content':brochure_system_prompt,
            },
            {
                'role':'user','content':get_brochure_user_prompt(company_name,url)
            }
        ],
    )
    
    result = response.choices[0].message.content
    
    return result
    


file = create_brochure("HuggingFace", "https://huggingface.co")

print(file)
