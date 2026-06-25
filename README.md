# Wireless and Sensor Systems Lab
Website source code for Wireless and Sensor Systems Lab

# Research lab website template

This website is built with [Jekyll](https://jekyllrb.com/).
It is derived from the great template provided by the
[Allan Lab](https://www.allanlab.org/aboutwebsite.html), at Leiden University.

## Setup

``` bash
brew install ruby
gem install bundler jekyll
```

Clone this repository, then install the dependencies:

``` bash
bundle install
```

## Run

Run the local webserver with:

``` bash
bundle exec jekyll serve
```

## Contribute

### Add a new member

New members are stored as markdown files under
[_pages/team/_posts](_pages/team/_posts).

Each new member `.md` file must look like this:

``` yaml
---
layout: member
category: staff
title: Researcher Name
image: researcher.png
role: Lab Director
permalink: 'team/researcher-name'
social:
    twitter: https://twitter.com/
    linkedin: https://www.linkedin.com/
    google-scholar: https://scholar.google.fr/
    github: https://github.com/
    website:
    orcid: https://orcid.org/
    research-gate: https://www.researchgate.net/
education:
 - Education
---

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
cupidatat non proident, sunt in culpa qui officia deserunt
mollit anim id est laborum.
```

### Add a new publication

Publications are stored as `.json` file under
[_data/publications.json](_data/publications.json).
This json file is exported from [Zotero](https://www.zotero.org/)
bibliography tool.

Just add a new entry to the list like this:

``` json
{
  "id": "http://zotero.org/groups/2386072/items/NU9LTX7C",
  "type": "article-journal",
  "title": "Foo",
  "container-title": "IEEE Transactions on Medical Imaging",
  "page": "448-459",
  "volume": "38",
  "issue": "2",
  "source": "IEEE Xplore",
  "abstract": "Bar",
  "DOI": "10.1109/TMI.2018.2865709",
  "author": [
    {
      "family": "",
      "given": ""
    },
  ],
  "issued": {
    "date-parts": [
      [
        "2019",
        2
      ]
    ]
  }
}
```

### Add news

News are stored as `.yml` file under [_data/news.yml](_data/news.yml).

An entry looks like the following:

```yaml
- date: 03/09/19
  title: "Something great"
  tags:
    - some
    - tags
  content: Lorem ipsum dolor sit amet, consectetur adipiscing elit,
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Eu turpis egestas pretium aenean. Luctus venenatis lectus magna fringilla
    urna porttitor. Lorem ipsum dolor sit amet. Pellentesque massa placerat
    duis ultricies. Commodo viverra maecenas accumsan lacus vel.
```

### Auto-Sync News & Publications (Weekly)

The website automatically checks the advisor's personal website every Sunday at 00:00 UTC using a GitHub Actions workflow. The sync pipeline:
1. Scrapes `https://people.cs.umass.edu/~phuc/`.
2. Uses OpenRouter (`nvidia/nemotron-3-nano-30b-a3b:free`) to convert news announcements into YAML blocks and new citations into BibTeX.
3. Merges the new items into `_data/news.yml` and `_data/publications.bib` after performing a title-similarity deduplication check.
4. Automatically runs `scripts/bib2json.py` to compile `publications.json`.
5. Commits and pushes the updates to the repository.

* **Files**: `scripts/sync_advisor_data.py` & `.github/workflows/sync-advisor.yml`
* **Secrets Required**: `OPENROUTER_API_KEY` (must be set in repository secrets).

### Auto-Submit Publications (via GitHub Issue)

To add a publication that is not on your advisor's website:
1. Go to the repository's **Issues** tab and click **New Issue**.
2. Choose the **Add Publication** template.
3. Paste the raw citation details (authors, title, venue, year, etc.) and submit.
4. The GitHub Action will use the LLM to format it into BibTeX, merge it into the bibliography, compile the JSON, and close the issue automatically.

* **Files**: `scripts/add_pub_from_issue.py` & `.github/workflows/add-publication-issue.yml`
* **Secrets Required**: `OPENROUTER_API_KEY`

### Auto-Submit News (via GitHub Issue)

To prepend a manual news item directly:
1. Go to the repository's **Issues** tab and click **New Issue**.
2. Choose the **Add News** template.
3. Paste the news text details and submit.
4. The GitHub Action will use the LLM to format it into a YAML block, prepend it to `_data/news.yml`, and close the issue automatically.

* **Files**: `scripts/add_news_from_issue.py` & `.github/workflows/add-news-issue.yml`
* **Secrets Required**: `OPENROUTER_API_KEY`

### Edit template

We use [Bootstrap](https://getbootstrap.com/) for designing the website.
Feel free to modify either the [_pages](_pages/) or the
[_layouts](_layouts/) components.
