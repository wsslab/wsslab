#!/usr/bin/env python3
import os
import re
import urllib.request
import urllib.error
import json
import yaml
from pathlib import Path
from bs4 import BeautifulSoup

ADVISOR_URL = "https://people.cs.umass.edu/~phuc/"
MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free"

def fetch_html(url):
    """Fetch HTML content from the given URL"""
    print(f"Fetching advisor website: {url}")
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error fetching URL: {e}")
        raise e

def call_openrouter(prompt, json_mode=False):
    """Call OpenRouter API with a free model"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://wsslab.org", # Required by OpenRouter
        "X-Title": "WSSL Sync Script"
    }
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    if json_mode:
        data["response_format"] = {"type": "json_object"}
        
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

def parse_news(html_content):
    """Parse the 5 most recent news items from the advisor's website using OpenRouter"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    heading = soup.find(string=lambda t: t and 'Selected News!' in t)
    if not heading:
        print("Could not find 'Selected News!' heading on advisor page.")
        return []
        
    h2 = heading.find_parent('h2')
    if not h2:
        print("Could not find parent h2 of news heading.")
        return []
        
    div = h2.find_next_sibling('div', class_='col-md-10')
    if not div:
        print("Could not find news list container.")
        return []
        
    ul = div.find('ul')
    if not ul:
        print("Could not find news list ul element.")
        return []
        
    raw_items = str(ul).split('<li>')
    cleaned_items = []
    
    # Skip the first element which is the opening <ul> tag
    for item in raw_items[1:]:
        item_clean = item.replace('</li>', '').replace('</ul>', '').strip()
        if item_clean:
            cleaned_items.append("<li>" + item_clean)
            
    # Take only the 5 most recent items
    cleaned_items = cleaned_items[:5]
    news_html_block = "\n".join(cleaned_items)
    
    prompt = f"""
    You are an assistant parsing unstructured website updates.
    Below is a list of the 5 most recent news items (as HTML list items) from a professor's personal website.
    Extract the news updates and return them in a JSON object with a single key "news" containing a list of items.
    Each item must have:
    - "date": formatted as "MM/YYYY" (e.g. 03/2026 or 12/2025)
    - "content": the description text (without HTML tags, but include clean text).
      CRITICAL instructions:
      1. Remove any leading date prefixes (like "03 - 2026:" or "02 - 2026:") from this text so it starts directly with the news description.
      2. Since this news is for the official lab website (not the advisor's personal website), convert any first-person pronouns referencing the advisor (like "I", "my", "me") into team-oriented or third-person pronouns (like "We", "our", "us", "Prof. Nguyen", or "WSSL Lab").
    - "highlights": (optional) list of objects containing:
        - "content": exact phrase to highlight (must match a substring of 'content')
        - "url": (optional) URL associated with that highlight from the href attribute
        
    HTML:
    {news_html_block}
    
    Return ONLY valid JSON.
    """
    
    print("Sending top 5 news items to OpenRouter...")
    response_text = call_openrouter(prompt, json_mode=True)
    try:
        parsed_data = json.loads(response_text)
        return parsed_data.get("news", [])
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {response_text}")
        raise e

def parse_publications(html_content):
    """Parse publication citation lines and convert to BibTeX format using OpenRouter"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find list items or paragraphs that look like citations
    # The publications on the page are under list structures or containing titles/venues
    # Let's extract text that contains paper links or conference names
    paragraphs = []
    for p in soup.find_all(['p', 'li']):
        text = p.get_text().strip()
        # Look for typical publication signs: brackets, author names, years
        if any(keyword in text.lower() for keyword in ["sensys", "mobisys", "mobicom", "nature", "ieee", "acm"]):
            paragraphs.append(text)
            
    # Let's deduplicate paragraphs
    unique_paragraphs = list(dict.fromkeys(paragraphs))
    cleaned_text = "\n\n".join(unique_paragraphs[:100]) # Top 100 items
    
    prompt = f"""
    You are a research publication parser. 
    Below are publication citation listings from a professor's website.
    Identify all actual publications (ignore general news or bio text).
    Convert each publication into a standard BibTeX entry (e.g. @inproceedings or @article).
    Make sure each entry has fields like title, author, booktitle/journal, year, doi (if present), and url (if present).
    Use a clean, unique key for each entry (e.g. author_lastname_year_firstwordoftitle).
    
    Return ONLY the raw BibTeX entries separated by two newlines. Do not include markdown code block formatting (like ```bibtex).
    
    Citations text:
    {cleaned_text}
    """
    
    print("Sending publications section to OpenRouter...")
    bibtex_response = call_openrouter(prompt, json_mode=False)
    # Clean markdown wrappers if any were returned despite instructions
    bibtex_response = re.sub(r'^```(bibtex)?', '', bibtex_response, flags=re.IGNORECASE)
    bibtex_response = re.sub(r'```$', '', bibtex_response)
    return bibtex_response.strip()

def merge_news(scraped_news, news_file_path):
    """Merge newly scraped news into the existing news.yml, preserving manual entries"""
    if not scraped_news:
        print("No scraped news to merge.")
        return
        
    print(f"Loading existing news from {news_file_path}")
    existing_news = []
    if news_file_path.exists():
        with open(news_file_path, 'r', encoding='utf-8') as f:
            existing_news = yaml.safe_load(f) or []
            
    # Normalize strings for robust deduplication comparison
    def normalize(text):
        return re.sub(r'[^a-z0-9]', '', text.lower())
        
    existing_normalized = [normalize(n.get('content', '')) for n in existing_news]
    
    added_count = 0
    for item in scraped_news:
        content = item.get('content', '')
        if not content:
            continue
            
        norm_content = normalize(content)
        # Check if this item (or a highly similar one) already exists
        is_duplicate = False
        for ex_norm in existing_normalized:
            # Substring matching to catch minor styling differences
            if norm_content in ex_norm or ex_norm in norm_content:
                is_duplicate = True
                break
                
        if not is_duplicate:
            # Prepend new item (reverse chronological)
            existing_news.insert(0, item)
            existing_normalized.append(norm_content)
            added_count += 1
            print(f"New news item added: [{item.get('date')}] {content[:60]}...")
            
    if added_count > 0:
        def get_date_key(item):
            date_str = str(item.get("date", ""))
            match = re.match(r'(\d{1,2})/(\d{4})', date_str)
            if match:
                return (int(match.group(2)), int(match.group(1)))
            match_other = re.match(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', date_str)
            if match_other:
                year_val = match_other.group(3)
                year = int(year_val) + (2000 if len(year_val) == 2 else 0)
                return (year, int(match_other.group(2)), int(match_other.group(1)))
            return (0, 0)
        
        existing_news.sort(key=get_date_key, reverse=True)
        with open(news_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(existing_news, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"Successfully added {added_count} new news items to {news_file_path}")
    else:
        print("No new news items detected.")

def merge_publications(scraped_bibtex, bib_file_path):
    """Merge new BibTeX entries into publications.bib if they don't already exist"""
    if not scraped_bibtex:
        print("No scraped publications to merge.")
        return 0
        
    print(f"Loading existing publications from {bib_file_path}")
    existing_bib_content = ""
    if bib_file_path.exists():
        with open(bib_file_path, 'r', encoding='utf-8') as f:
            existing_bib_content = f.read()
            
    # Find all entries (e.g. @article{...} or @inproceedings{...}) in the new bibtex string
    new_entries = re.findall(r'@\w+\{[^@]*\}', scraped_bibtex, re.DOTALL)
    
    added_count = 0
    appended_entries = []
    
    for entry in new_entries:
        # Extract title field
        title_match = re.search(r'title\s*=\s*\{+([^}]+)\}+', entry, re.IGNORECASE)
        if not title_match:
            # Try double quotes format title = "..."
            title_match = re.search(r'title\s*=\s*"([^"]+)"', entry, re.IGNORECASE)
            
        if title_match:
            title_val = title_match.group(1).lower().strip()
            # Clean title
            title_clean = re.sub(r'[{}]', '', title_val)
            title_words = re.sub(r'[^a-z0-9\s]', '', title_clean).split()
            # If title is very short, it's not valid
            if len(title_words) < 3:
                continue
                
            # Check if this title is in existing publications
            # Using keyword matching for robustness (e.g. case/whitespace variations)
            title_phrase = " ".join(title_words[:5]) # Match first 5 words
            if title_phrase not in re.sub(r'[^a-z0-9\s]', '', existing_bib_content.lower()):
                appended_entries.append(entry.strip())
                added_count += 1
                print(f"New publication added: {title_clean[:60]}...")
                
    if added_count > 0:
        with open(bib_file_path, 'a', encoding='utf-8') as f:
            for entry in appended_entries:
                f.write("\n\n" + entry)
        print(f"Successfully appended {added_count} new entries to {bib_file_path}")
    else:
        print("No new publications detected.")
        
    return added_count

def main():
    # Setup paths
    project_root = Path(__file__).parent.parent
    news_file = project_root / '_data' / 'news.yml'
    bib_file = project_root / '_data' / 'publications.bib'
    
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY environment variable is not set. Exiting.")
        return
        
    try:
        html = fetch_html(ADVISOR_URL)
        
        # 1. Sync News
        scraped_news = parse_news(html)
        merge_news(scraped_news, news_file)
        
        # 2. Sync Publications
        scraped_bib = parse_publications(html)
        merge_publications(scraped_bib, bib_file)
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        # Exit with code 1 so that CI/CD workflow fails visibly
        exit(1)

if __name__ == '__main__':
    main()
