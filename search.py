import requests
from collections import defaultdict
import time
import os

# Prefer the S2_API_KEY environment variable; fall back to config.py.
API_KEY = os.environ.get("S2_API_KEY")
if not API_KEY:
    try:
        from config import API_KEY
    except ImportError:
        API_KEY = None
        print("Warning: no Semantic Scholar API key (set S2_API_KEY); requests will be heavily rate limited.")

MIN_INTERVAL = 1.05  # keyed accounts start at 1 request/second
MAX_BACKOFF = 60
_last_request = 0.0

def _get_with_backoff(url, params, headers):
    """GET with client-side throttling and exponential backoff on 429/5xx."""
    global _last_request
    delay = 1
    while True:
        wait = MIN_INTERVAL - (time.time() - _last_request)
        if wait > 0:
            time.sleep(wait)
        _last_request = time.time()
        response = requests.get(url, params=params, headers=headers, allow_redirects=True)
        if response.status_code == 200:
            return response
        if response.status_code == 429 or response.status_code >= 500:
            retry_after = response.headers.get('Retry-After')
            sleep_for = int(retry_after) if retry_after and retry_after.isdigit() else delay
            print(f"HTTP {response.status_code}. Retrying after {sleep_for} seconds...")
            time.sleep(sleep_for)
            delay = min(delay * 2, MAX_BACKOFF)
        else:
            response.raise_for_status()

def search_semantic_scholar(query, coarse_domain, limit=5, year=None, baseline=False):
    url = "http://api.semanticscholar.org/graph/v1/snippet/search"
    # Valid Semantic Scholar domains
    valid_domains = {
        "Computer Science", "Medicine", "Chemistry", "Biology", "Materials Science",
        "Physics", "Geology", "Psychology", "Art", "History", "Geography",
        "Sociology", "Business", "Political Science", "Economics", "Philosophy",
        "Mathematics", "Engineering", "Environmental Science",
        "Agricultural and Food Sciences", "Education", "Law", "Linguistics"
    }
    query_params = {"query": query, "limit": limit}

    if coarse_domain in valid_domains:
        query_params["fieldsOfStudy"] = coarse_domain
    if year is not None:
        query_params["year"] = f"-{year-1}"

    if baseline:
        headers = {"x-api-key": API_KEY} if API_KEY else {}
    else:
        headers = {"x-api-key": API_KEY} if API_KEY else {}
    
    print(f"\t -Searching Semantic Scholar for query: {query} in domain: {coarse_domain}.")

    response = _get_with_backoff(url, query_params, headers)
    
    if response.status_code == 200:
        return_response = response.json()['data']
        if len(return_response) == 0:
            print(f"\t -No results found for query: {query} in domain: {coarse_domain}.")
        return return_response
    else:
        response.raise_for_status()

def fetch_paper_details(paper_id):
    url = f"http://api.semanticscholar.org/graph/v1/paper/CorpusId:{paper_id}"
    params = {
        "fields": "title,abstract"
    }
    headers = {"x-api-key": API_KEY} if API_KEY else {}
    
    return _get_with_backoff(url, params, headers).json()

def collect_snippets(response):
    snippets = defaultdict(list)
    for item in response:
        title = item.get('paper', {}).get('title', '')
        text = item.get('snippet', {}).get('text', '')
        if title.strip() == text.strip():
            paper_info = fetch_paper_details(item.get('paper', {}).get('corpusId', ''))
            text = paper_info.get('abstract', '')
        
        if text:
            snippets[title].append(text.strip())
        else:
            continue
    
    return snippets