import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_offer_links(keyword="data engineer"):
    query = quote_plus(keyword)
    url = f"https://justjoin.it/job-offers/all-locations/data?keyword={query}"

    print(f"[DEBUG] URL: {url}")

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("⚠️ Nie udało się pobrać strony")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    offer_links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.startswith("/job-offer/") and "?" not in href:
            full_url = "https://justjoin.it" + href
            if full_url not in offer_links:
                offer_links.append(full_url)

    print(f"[DEBUG] Znaleziono {len(offer_links)} ofert")
    return offer_links