import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.114 Safari/537.36"
    )
}

BASE_URL = "https://justjoin.it"

def extract_tech_stack(offer_url: str) -> list[str]:
    for _ in range(3):  # Retry mechanism
        try:
            response = requests.get(offer_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            stack_elements = soup.select("div.MuiBox-root h4.MuiTypography-root.MuiTypography-subtitle2")
            return [el.get_text(strip=True) for el in stack_elements if el.get_text(strip=True)]
        except Exception:
            time.sleep(1)
    return []

def fetch_offer_links(keyword: str = "PHP", max_offset: int = 2000, fine_scan_limit: int = 30) -> list[str]:
    all_links = []
    seen_links = set()
    step = 100

    def get_links(offset: int) -> list[str]:
        url = f"{BASE_URL}/job-offers/all-locations?keyword={quote(keyword)}"
        if offset:
            url += f"&from={offset}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            links = [BASE_URL + a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("/job-offer/")]
            print(f"[DEBUG] Scraping: {url} | Links found: {len(links)}")
            return links
        except Exception as e:
            print(f"[ERROR] {url} failed with {e}")
            return []

    offset = 0
    while offset < max_offset:
        links = get_links(offset)
        new_links = [l for l in links if l not in seen_links]
        if not new_links:
            print("[STOP] Brak nowych wyników – kończę.")
            break
        all_links.extend(new_links)
        seen_links.update(new_links)
        offset += step

    # Fine scan if needed
    for fine_offset in range(offset - step + 1, offset + fine_scan_limit):
        links = get_links(fine_offset)
        new_links = [l for l in links if l not in seen_links]
        if not new_links:
            break
        all_links.extend(new_links)
        seen_links.update(new_links)

    print(f"[DEBUG] Unikalnych linków: {len(seen_links)}")
    return list(seen_links)

def scrape_offers_with_stack(links: list[str]) -> list[dict]:
    offers = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(extract_tech_stack, url): url for url in links}
        for future in as_completed(futures):
            url = futures[future]
            try:
                stack = future.result()
                offers.append({"url": url, "tech_stack": stack})
                print(f"[STACK ✅] {url} → {stack}")
            except Exception as e:
                print(f"[STACK ❌] {url}: {e}")
    return offers

# Execute the full scrape process
links = fetch_offer_links()
offers = scrape_offers_with_stack(links)
import pandas as pd
import ace_tools as tools; tools.display_dataframe_to_user(name="Scraped PHP Offers", dataframe=pd.DataFrame(offers))
