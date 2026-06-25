#!/usr/bin/env python3
import os
import re
import urllib.request
import urllib.error
import json
from pathlib import Path

MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free"

def call_openrouter(prompt):
    """Call OpenRouter API with the free Nemotron model"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://wsslab.org", # Required by OpenRouter
        "X-Title": "WSSL Issue Sync Script"
    }
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if "choices" not in res_data or not res_data["choices"]:
                raise ValueError(f"Unexpected response from OpenRouter: {res_data}")
            return res_data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e else ""
        print(f"HTTP Error: {e.code} - {e.reason}\nBody: {error_body}")
        raise e

def convert_to_bibtex(raw_text):
    """Parse raw citation text and convert to a BibTeX entry via OpenRouter"""
    prompt = f"""
    You are a bibliography formatter.
    Convert the following citation information into a single, valid BibTeX entry (e.g. @inproceedings or @article).
    Ensure it contains standard fields: title, author, booktitle (or journal), year, doi (if present), and url (if present).
    Generate a clean and unique key for the entry (e.g. author_lastname_year_firstwordoftitle).
    
    Return ONLY the raw BibTeX entry. Do not include markdown code blocks (like ```bibtex).
    
    Citation info:
    {raw_text}
    """
    
    print("Calling OpenRouter to parse citation...")
    bibtex_response = call_openrouter(prompt)
    # Clean markdown wrappers if any were returned despite instructions
    bibtex_response = re.sub(r'^```(bibtex)?', '', bibtex_response, flags=re.IGNORECASE)
    bibtex_response = re.sub(r'```$', '', bibtex_response)
    return bibtex_response.strip()

def merge_publication(scraped_bibtex, bib_file_path):
    """Merge new BibTeX entry into publications.bib if not already present"""
    if not scraped_bibtex:
        raise ValueError("LLM returned empty BibTeX entry")
        
    print(f"Loading existing publications from {bib_file_path}")
    existing_bib_content = ""
    if bib_file_path.exists():
        with open(bib_file_path, 'r', encoding='utf-8') as f:
            existing_bib_content = f.read()
            
    # Extract title field to check for duplicates
    title_match = re.search(r'title\s*=\s*\{+([^}]+)\}+', scraped_bibtex, re.IGNORECASE)
    if not title_match:
        # Try double quotes format title = "..."
        title_match = re.search(r'title\s*=\s*"([^"]+)"', scraped_bibtex, re.IGNORECASE)
        
    if not title_match:
        # If we couldn't parse the title, we append it anyway but print a warning
        print("⚠️ Warning: Could not find title in generated BibTeX. Appending anyway.")
        with open(bib_file_path, 'a', encoding='utf-8') as f:
            f.write("\n\n" + scraped_bibtex)
        return
        
    title_val = title_match.group(1).lower().strip()
    title_clean = re.sub(r'[{}]', '', title_val)
    title_words = re.sub(r'[^a-z0-9\s]', '', title_clean).split()
    
    if len(title_words) < 3:
        raise ValueError(f"Extracted title is too short: '{title_clean}'")
        
    title_phrase = " ".join(title_words[:5])
    if title_phrase in re.sub(r'[^a-z0-9\s]', '', existing_bib_content.lower()):
        print(f"🛑 Duplicate detected: Title '{title_clean}' already exists in bibliography.")
        return False
        
    with open(bib_file_path, 'a', encoding='utf-8') as f:
        f.write("\n\n" + scraped_bibtex)
    print(f"✅ Successfully appended new publication: {title_clean}")
    return True

def main():
    project_root = Path(__file__).parent.parent
    bib_file = project_root / '_data' / 'publications.bib'
    
    issue_body = os.environ.get("ISSUE_BODY")
    if not issue_body:
        raise ValueError("ISSUE_BODY environment variable is empty or not set.")
        
    # Remove markdown comments if any are default in issue template
    issue_body = re.sub(r'<!--.*?-->', '', issue_body, flags=re.DOTALL).strip()
    
    bibtex = convert_to_bibtex(issue_body)
    success = merge_publication(bibtex, bib_file)
    if not success:
        # We can exit with code 0 but print a message so the issue workflow knows it was a duplicate
        print("Deduplication logic skipped insertion.")

if __name__ == '__main__':
    main()
