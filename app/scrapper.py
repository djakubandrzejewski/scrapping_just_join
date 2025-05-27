import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import List, Optional

headers = {
    "User-Agent": "Mozilla/5.0"
}


def get_offer_links(keyword: str = "", categories: Optional[List[str]] = None) -> List[str]:
    """
    Scrapes job offer links from JustJoin based on keyword and selected categories.

    Args:
        keyword (str): The search keyword (e.g. "python", "data engineer")
        categories (List[str], optional): List of category slugs. If None, uses "all".

    Returns:
        List[str]: List of unique job offer URLs.
    """
    if not categories:
        categories = ["all"]

    all_links = set()

    for cat in categories:
        url = f"https://justjoin.it/job-offers/all-locations/{cat}"
        if keyword:
            url += f"?keyword={quote(keyword)}"

        print(f"[DEBUG] Scraping URL: {url}")
        try:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                print(f"⚠️ Błąd pobierania: {url}")
                continue

            soup = BeautifulSoup(res.text, "html.parser")

            for a in soup.find_all("a", href=True):
                href = a['href']
                if href.startswith("/job-offer/") and "?" not in href:
                    full_url = "https://justjoin.it" + href
                    all_links.add(full_url)

        except Exception as e:
            print(f"❌ Wyjątek przy {url}: {e}")
            continue

    return list(all_links)