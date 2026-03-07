#!/usr/bin/env python3
"""
Convert BibTeX publications to JSON format
Usage: python scripts/bib2json.py
"""

import json
import re
import sys
from pathlib import Path

def parse_author(author_str):
    """Parse author string into structured format"""
    authors = []
    # Split by 'and' but not '&'
    author_parts = re.split(r'\s+and\s+', author_str)

    for author in author_parts:
        author = author.strip()
        if ',' in author:
            # Format: "Last, First"
            parts = author.split(',', 1)
            family = parts[0].strip()
            given = parts[1].strip() if len(parts) > 1 else ""
        else:
            # Format: "First Last"
            parts = author.rsplit(' ', 1)
            given = parts[0].strip() if len(parts) > 1 else ""
            family = parts[1].strip() if len(parts) > 1 else author

        authors.append({
            "family": family,
            "given": given
        })

    return authors

def parse_bib_entry(entry_text):
    """Parse a single BibTeX entry"""
    # Extract entry type and key
    match = re.match(r'@(\w+)\{([^,]+),', entry_text)
    if not match:
        return None

    entry_type = match.group(1).lower()
    entry_key = match.group(2)

    # Map BibTeX types to CSL types
    type_mapping = {
        'article': 'article-journal',
        'inproceedings': 'paper-conference',
        'conference': 'paper-conference',
        'book': 'book',
        'misc': 'article'
    }

    result = {
        "id": "",
        "type": type_mapping.get(entry_type, "article-journal")
    }

    # Extract fields - handle nested braces
    fields = []
    for match in re.finditer(r'(\w+)\s*=\s*\{', entry_text):
        field_name = match.group(1)
        start = match.end()

        # Find matching closing brace
        brace_count = 1
        pos = start
        while brace_count > 0 and pos < len(entry_text):
            if entry_text[pos] == '{':
                brace_count += 1
            elif entry_text[pos] == '}':
                brace_count -= 1
            pos += 1

        field_value = entry_text[start:pos-1]
        fields.append((field_name, field_value))

    for field_name, field_value in fields:
        field_name = field_name.lower()
        field_value = field_value.strip()

        if field_name == 'title':
            # Remove extra braces used for capitalization protection
            field_value = re.sub(r'\{([^}]*)\}', r'\1', field_value)
            result['title'] = field_value

        elif field_name == 'author':
            result['author'] = parse_author(field_value)

        elif field_name in ['booktitle', 'journal']:
            result['container-title'] = field_value

        elif field_name == 'year':
            year = field_value
            result['issued'] = {"date-parts": [[year]]}

        elif field_name == 'month':
            # Add month to existing issued field
            month_map = {
                'jan': '1', 'feb': '2', 'mar': '3', 'apr': '4',
                'may': '5', 'jun': '6', 'jul': '7', 'aug': '8',
                'sep': '9', 'oct': '10', 'nov': '11', 'dec': '12'
            }
            month_num = month_map.get(field_value.lower(), field_value)
            if 'issued' in result and 'date-parts' in result['issued']:
                result['issued']['date-parts'][0].append(month_num)

        elif field_name == 'doi':
            result['DOI'] = field_value

        elif field_name == 'url':
            result['url'] = field_value
            if not result['id']:
                result['id'] = field_value

        elif field_name == 'note':
            result['note'] = field_value

        elif field_name == 'volume':
            result['volume'] = field_value

        elif field_name == 'number':
            result['number'] = field_value

    # Set ID from DOI if available and ID not set
    if 'DOI' in result and not result['id']:
        result['id'] = f"https://doi.org/{result['DOI']}"

    # Generate a default ID if still not set
    if not result['id']:
        result['id'] = f"#{entry_key}"

    return result

def convert_bib_to_json(bib_file, json_file):
    """Convert BibTeX file to JSON"""
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove comments
    content = re.sub(r'%.*$', '', content, flags=re.MULTILINE)

    # Split into entries
    entries = re.findall(r'@\w+\{[^@]*\}', content, re.DOTALL)

    publications = []
    for entry in entries:
        parsed = parse_bib_entry(entry)
        if parsed:
            publications.append(parsed)

    # Write JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(publications, f, indent=2, ensure_ascii=False)

    print(f"✅ Converted {len(publications)} publications from {bib_file} to {json_file}")

if __name__ == '__main__':
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    bib_file = project_root / '_data' / 'publications.bib'
    json_file = project_root / '_data' / 'publications.json'

    if not bib_file.exists():
        print(f"❌ Error: {bib_file} not found")
        sys.exit(1)

    convert_bib_to_json(bib_file, json_file)
