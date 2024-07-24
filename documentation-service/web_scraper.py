import requests
from bs4 import BeautifulSoup

def scrape_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract text content
    text = soup.get_text(separator=' ', strip=True)
    
    # Extract code snippets (assuming they're in <pre> or <code> tags)
    code_snippets = [code.get_text() for code in soup.find_all(['pre', 'code'])]
    
    return {
        'url': url,
        'text': text,
        'code_snippets': code_snippets
    }