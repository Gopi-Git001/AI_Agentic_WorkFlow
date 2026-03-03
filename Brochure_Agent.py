import os 
import requests
import json
from dotenv import load_dotenv
from IPython.display import Markdown,display,update_display
from openai import OpenAI
from bs4 import BeautifulSoup
from web_scraper import fetch_website_contents,fetch_website_links

load_dotenv(override=True)

def get_client(provider:str) -> OpenAI:
    
        base_url = os.getenv(f"{provider}_BASE_URL")
        api_key = os.getenv(f"{provider}_API_KEY")
        
        if not base_url or not api_key:
            raise ValueError(f"{provider}_BASE_URL or {provider}_API_KEY not found in environment")
         
        return OpenAI(base_url=base_url,api_key=api_key)
    

client = get_client("OPENAI")
MODEL = "gpt-4.1-mini"

# print(client)

# link_system_prompt = """
# You are the provided with a list of links found on webpage.
# You are able to decide which of the links would be most relevant to include in a brochure about the company,
# such as links to an About page, or a Company page, or a Careers/Jobs pages.
# You should respond in JSON as in this example:

# {
#     "links":[
#         {"type":"about page", "url":"https://full.url/goes/here/about"},
#         {"type":"careers page","url":"https://another.full.url/careers"}
#     ]
# }

# """

link_system_prompt = """
You are given a list of links found on a company's website.

Goal:
Select the BEST links needed to write a high-quality brochure with evidence-backed claims.

Hard requirements:
- Prefer pages that explicitly describe: products/features, docs, pricing, enterprise, customers/case studies, company/about, blog/news, and careers/jobs.
- Always try to include at least ONE link for each category if present:
  1) about/company/mission
  2) products/platform/overview (or equivalent)
  3) docs/documentation
  4) pricing/plans/enterprise
  5) customers/case-studies/stories/partners
  6) careers/jobs/hiring
- Exclude: terms, privacy, cookies, legal, email/mailto, social media, status pages, login/signup, and unrelated links.

Return STRICT JSON ONLY (no extra text), exactly:
{
  "links": [
    {"type": "about", "url": "https://full.url/..."},
    {"type": "products", "url": "https://full.url/..."}
  ]
}
"""





def user_link_prompt(url):
    user_prompt =f"""
Here is a list of links found on the website: {url}

Select the most relevant links for building a brochure.
Rules:
- Return ONLY JSON (no commentary).
- Use full https URLs (convert relative links to absolute).
- Do NOT include: Terms, Privacy, Legal, Cookies, mailto, social links, login/signup.

Links:
{{links_from_scraper}}
"""
    
    links = fetch_website_links(url)
    user_prompt += "\n".join(links)
    return user_prompt

def select_relevant_links(url):
    
    messages = [
        {"role":"system","content":link_system_prompt},
        {"role":"user","content":user_link_prompt(url)}
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        # response_format={"type":"json_object"},
        max_completion_tokens=400
    )
    
    result = response.choices[0].message.content
    links = json.loads(result)
    return links


# from urllib.parse import urljoin

# MUST_CONTAIN = [
#     "about", "company", "mission", "product", "platform",
#     "models", "datasets", "spaces", "docs", "documentation",
#     "enterprise", "pricing", "careers", "jobs",
#     "customers", "case-studies", "blog"
# ]
# def must_include_links(base_url: str, all_links: list[str], limit: int = 10) -> list[str]:
#     # convert relative → absolute and filter by keywords
#     urls = [urljoin(base_url, l) for l in all_links]
#     picked = []
#     for u in urls:
#         lu = u.lower()
#         if any(k in lu for k in MUST_CONTAIN):
#             picked.append(u)

#     # dedupe preserving order
#     out = []
#     for u in picked:
#         if u not in out:
#             out.append(u)

#     return out[:limit]

def fetch_page_and_all_relevant_links(url):
    relevant_links = select_relevant_links(url)
    output = []
    
    
    
    # --- NEW: force include important pages from raw scraped links ---
    # raw_links = fetch_website_links(url)
    # forced_urls = must_include_links(url, raw_links, limit=10)

    # # Convert forced_urls into same dict format + dedupe by url
    # existing = {item["url"] for item in relevant_links.get("links", []) if "url" in item}
    # for fu in forced_urls:
    #     if fu not in existing:
    #         relevant_links["links"].append({"type": "must_include", "url": fu})
    #         existing.add(fu)
    
    for link in relevant_links['links']:
        link_type = link['type']
        link_url = link['url']
        
        output.append(link_type)
        # output.append(fetch_website_contents(link_url))
        
        try:
            output.append(fetch_website_contents(link_url))
        except requests.exceptions.HTTPError as e:
            output.append(f"[Skipped: {link_url} returned an error: {e}]")
        except requests.exceptions.RequestException as e:
            output.append(f"[Skipped: {link_url} request failed: {e}]")
        
        print("FETCHING:", link_type, link_url)
        
    return "\n".join(output)



def build_page_extracts(url: str) -> str:
    parts = []

    # homepage
    try:
        parts.append(f"PAGE: homepage\nURL: {url}\n")
        parts.append(fetch_website_contents(url))
    except Exception as e:
        parts.append(f"PAGE: homepage\nURL: {url}\n[FAILED: {e}]")

    # relevant pages
    relevant_links = select_relevant_links(url)
    for link in relevant_links.get("links", []):
        t, u = link.get("type"), link.get("url")
        parts.append(f"\nPAGE: {t}\nURL: {u}\n")
        try:
            parts.append(fetch_website_contents(u))
        except Exception as e:
            parts.append(f"[FAILED: {e}]")

    return "\n".join(parts)

# brochure_prompt = """
# You are a assistant that analyze the content of several 
# relevant pages from a company website and creates a short brochure about the company for prospective customers,
# Investors and recruiters.
# Respond in markdown without code blocks.
# Include details of company culture,customers and careers/jobs if you have the information.
# """




brochure_prompt = """
You are a brochure-writing assistant (KING MODE, 10/10 QUALITY BAR).

Goal:
Write a short brochure using ONLY the provided website extracts (homepage + relevant pages), aimed at Customers, Investors, and Recruiters.

Non-negotiable rules:
- Output must be Markdown and MUST NOT include fenced code blocks (no ```).
- Use ONLY the provided website content. Do NOT invent facts, metrics, customers, partners, pricing, funding, locations, or claims.
- NO "implied" / "likely" / "probably" / "suggests" wording. If it is not directly supported, it must be marked as not stated.
- Every non-trivial claim MUST be backed by a direct quote from the extracts.
- Quotes must be short (<= 20 words each) and copied verbatim from the provided text.
- Each section must have at least ONE UNIQUE quote that does not appear in any other section,
  except sections that are "Not stated on the website content provided."
- If a section lacks a supporting quote, write ONLY: "Not stated on the website content provided."
- If content conflicts across pages, do not guess. Mark: "Conflicting info on site" and show quotes from both sides.
- If the extracts include sensitive info (keys, tokens, private emails/phones), redact as [REDACTED] and do not repeat it.

Required output structure (exact order):
# {company_name} — Brochure

## Overview
- 1–2 sentence summary strictly supported by quotes.
**Evidence:**
- “...”
- “...” (optional)

## Products / Services
- Bullet list of offerings ONLY if supported by quotes.
**Evidence:**
- “...”

## Who it’s for
- Bullet list of audiences/use cases ONLY if supported by quotes.
**Evidence:**
- “...”

## Differentiators
- Bullet list of differentiators ONLY if supported by quotes.
**Evidence:**
- “...”

## Culture / Values (if available)
- Bullet list ONLY if supported by quotes.
**Evidence:**
- “...”

## Customers / Partners (if available)
- List ONLY if supported by quotes (names must appear in text).
**Evidence:**
- “...”

## Careers / Jobs (if available)
- Include hiring/careers details ONLY if supported by quotes.
**Evidence:**
- “...”

## Quick facts from the site
- 4–8 bullets, strictly factual, each supported by the extracts.
**Evidence:**
- Include 1–3 quotes that support multiple facts (still <=20 words each).

## Open questions / missing info
- Bullet list of the most important missing details, especially:
  products, target audiences, pricing, customers, hiring, locations, compliance.

Quality checks you MUST pass:
- No section contains claims without direct quote evidence.
- No quote is reused across sections when a unique quote is available.
- No "implied" evidence or meta statements like "not explicitly stated but..."


Hard rule:
- You MUST NOT include any bullet point unless you can provide a direct quote from the extracts supporting it.
- If you cannot find a quote for Products/Services or Who it’s for, output ONLY: "Not stated on the website content provided."
- Do not add notes that justify inferences (no “implied”, no “extracts confirm”).

- Do NOT use technical implementation details (scripts, CSS libraries, meta tags, analytics, fonts) as brochure facts.
  Only use human-facing product/marketing/careers text.
- In “Quick facts”, include ONLY business facts (mission, offerings, audiences, pricing, customers, hiring, locations).

"""




def get_brochure_user_prompt(company_name,url,page_extracts):
    
    # user_prompt =f"""
    # You are looking at a company called :{company_name}-
    # Here are the contents of its landing page and others relevant pages;
    # use this information to build a short brochure of the company in the markdown code blocks .\n\n
    # """
    
    
    user_prompt = f"""
Create a short brochure in Markdown (NO code blocks) using ONLY the website content below.

Company name:
{company_name}

Website content (landing page + relevant pages):
{page_extracts}

Constraints:
- Audience priority: Customers > Investors > Recruiters
- Length: 400–700 words
- Tone: Professional, clear, modern

Follow this exact output order:
# {company_name} — Brochure
## Overview
## Products / Services
## Who it’s for
## Differentiators
## Culture / Values (if available)
## Customers / Partners (if available)
## Careers / Jobs (if available)
## Quick facts from the site
## Open questions / missing info
"""
    
    user_prompt += fetch_page_and_all_relevant_links(url)
    
    user_prompt = user_prompt[:80_000]
    
    return user_prompt


def create_brochure(company_name,url):
    
    page_extracts = build_page_extracts(url)
    messages = [
        {"role":'system','content':brochure_prompt},
        {'role':'user','content':get_brochure_user_prompt(company_name,url,page_extracts)}
    ]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=900
        
    )
    result =  response.choices[0].message.content
    
    return result

file = create_brochure("HuggingFace", "https://huggingface.co")

print(file)
