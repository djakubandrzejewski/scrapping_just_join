import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_offer_links():
    url = "https://justjoin.it/job-offers/all-locations/data?keyword=data+engineer"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    offer_links = []

    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.startswith("/job-offer/") and "?" not in href:
            full_url = "https://justjoin.it" + href
            if full_url not in offer_links:
                offer_links.append(full_url)

    return offer_links