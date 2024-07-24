import xml.etree.ElementTree as ET
import requests

def process_sitemap(sitemap_url, user_guidance):
    response = requests.get(sitemap_url)
    root = ET.fromstring(response.content)

    urls = []
    for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        if any(guide in url.text for guide in user_guidance):
            urls.append(url.text)

    return urls