#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from openai import OpenAI

# Your existing module
from web_scraper import fetch_website_contents, fetch_website_links


# ----------------------------
# Config
# ----------------------------

MODEL = os.getenv("BROCHURE_MODEL", "gpt-4.1-mini")

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
""".strip()

brochure_system_prompt = """
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

Hard rule:
- You MUST NOT include any bullet point unless you can provide a direct quote from the extracts supporting it.
- If you cannot find a quote for Products/Services or Who it’s for, output ONLY: "Not stated on the website content provided."
- Do not add notes that justify inferences (no “implied”, no “extracts confirm”).

- Do NOT use technical implementation details (scripts, CSS libraries, meta tags, analytics, fonts) as brochure facts.
  Only use human-facing product/marketing/careers text.
- In “Quick facts”, include ONLY business facts (mission, offerings, audiences, pricing, customers, hiring, locations).
""".strip()


# ----------------------------
# Helpers
# ----------------------------

def get_client(provider: str) -> OpenAI:
    base_url = os.getenv(f"{provider}_BASE_URL")
    api_key = os.getenv(f"{provider}_API_KEY")
    if not base_url or not api_key:
        raise ValueError(f"{provider}_BASE_URL or {provider}_API_KEY not found in environment")
    return OpenAI(base_url=base_url, api_key=api_key)


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("Empty URL.")
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    return url


def prompt_if_missing(value: Optional[str], label: str) -> str:
    if value and value.strip():
        return value.strip()
    return input(f"{label}: ").strip()


def safe_scrape(fn, *args, retries: int = 2, backoff_s: float = 0.8, **kwargs):
    last_err = None
    for i in range(retries + 1):
        try:
            return fn(*args, **kwargs)
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            last_err = e
            if i < retries:
                time.sleep(backoff_s * (2 ** i))
            else:
                raise
    raise last_err  # unreachable


def user_link_prompt(url: str, links: List[str]) -> str:
    prompt = f"""
Here is a list of links found on the website: {url}

Select the most relevant links for building a brochure.
Rules:
- Return ONLY JSON (no commentary).
- Use full https URLs (convert relative links to absolute).
- Do NOT include: Terms, Privacy, Legal, Cookies, mailto, social links, login/signup.

Links:
"""
    prompt += "\n".join(links)
    return prompt.strip()


def select_relevant_links(client: OpenAI, url: str, links: List[str]) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": link_system_prompt},
        {"role": "user", "content": user_link_prompt(url, links)},
    ]
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=400,
    )
    raw = resp.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Defensive fallback: if model returns non-JSON, fail loudly with context.
        raise ValueError(f"Link selection did not return valid JSON. Got:\n{raw}")


def build_page_extracts(client: OpenAI, url: str, max_pages: int = 8) -> str:
    parts: List[str] = []

    # Homepage
    parts.append(f"PAGE: homepage\nURL: {url}\n")
    try:
        parts.append(safe_scrape(fetch_website_contents, url))
    except Exception as e:
        parts.append(f"[FAILED: {e}]")

    # Collect links
    all_links = safe_scrape(fetch_website_links, url)
    selected = select_relevant_links(client, url, all_links)
    links = selected.get("links", [])

    # Limit pages to avoid huge prompts/cost
    links = links[:max_pages]

    for link in links:
        t = link.get("type", "unknown")
        u = link.get("url")
        if not u:
            continue

        parts.append(f"\nPAGE: {t}\nURL: {u}\n")
        try:
            parts.append(safe_scrape(fetch_website_contents, u))
        except Exception as e:
            parts.append(f"[FAILED: {e}]")

    return "\n".join(parts)


def build_brochure_user_prompt(company_name: str, url: str, page_extracts: str) -> str:
    prompt = f"""
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
""".strip()

    # Hard cap to avoid overlong requests
    return prompt[:80_000]


def create_brochure(client: OpenAI, company_name: str, url: str) -> str:
    extracts = build_page_extracts(client, url)
    messages = [
        {"role": "system", "content": brochure_system_prompt},
        {"role": "user", "content": build_brochure_user_prompt(company_name, url, extracts)},
    ]
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=900,
    )
    return resp.choices[0].message.content


def derive_company_name_from_url(url: str) -> str:
    # Best-effort fallback: use hostname
    from urllib.parse import urlparse
    host = urlparse(url).netloc
    host = host.replace("www.", "")
    return host.split(":")[0]


def main() -> int:
    load_dotenv(override=True)

    parser = argparse.ArgumentParser(description="Generate a brochure from a company website URL.")
    parser.add_argument("--url", help="Website URL (e.g., https://huggingface.co)")
    parser.add_argument("--company", help="Company name (optional)")
    parser.add_argument("--out", help="Write brochure to file instead of stdout")
    args = parser.parse_args()

    try:
        url = prompt_if_missing(args.url, "Enter website URL")
        url = normalize_url(url)

        company = args.company.strip() if args.company else ""
        if not company:
            # Ask once, but not required
            company = input("Enter company name (optional, press Enter to use domain): ").strip()
        if not company:
            company = derive_company_name_from_url(url)

        client = get_client("OPENAI")
        brochure = create_brochure(client, company, url)

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(brochure)
            print(f"Wrote brochure to: {args.out}", file=sys.stderr)
        else:
            print(brochure)

        return 0

    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())