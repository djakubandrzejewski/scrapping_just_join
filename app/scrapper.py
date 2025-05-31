import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from requests.exceptions import RequestException

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.114 Safari/537.36"
    )
}

BASE_URL = "https://justjoin.it"

def extract_tech_stack(offer_url: str, retries: int = 3, delay: float = 2.0) -> list[str]:
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(offer_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            stack_elements = soup.select("div.MuiBox-root h4.MuiTypography-root.MuiTypography-subtitle2")
            stack = [el.get_text(strip=True) for el in stack_elements if el.get_text(strip=True)]
            print(f"[STACK ✅] {offer_url} → {stack}")
            return stack
        except Exception as e:
            print(f"[STACK RETRY {attempt}/{retries}] {offer_url} → {e}")
            time.sleep(delay)
    print(f"[STACK ❌] {offer_url} → NIEUDANE")
    return []

def get_offer_links(keyword: str = "", category: str = "all") -> List[Dict[str, str]]:
    offers = []
    offset = 0
    step = 100
    max_offset = 2000
    all_links = []

    def fetch_links(offset_val: int, retries: int = 3, delay: float = 2.0) -> List[str]:
        url = f"{BASE_URL}/job-offers/all-locations"
        if category != "all":
            url += f"/{quote(category)}"
        params = {"keyword": keyword, "from": offset_val} if offset_val else {"keyword": keyword}
        param_str = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
        full_url = f"{url}?{param_str}"
        print(f"[DEBUG] Scraping: {full_url} | Offset: {offset_val}")

        for attempt in range(1, retries + 1):
            try:
                res = requests.get(full_url, headers=HEADERS, timeout=10)
                res.raise_for_status()
                soup = BeautifulSoup(res.text, "html.parser")
                links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("/job-offer/")]
                full_links = [BASE_URL + href for href in links]
                print(f"[INFO]  -> Liczba /job-offer/ linków: {len(full_links)}")
                return full_links
            except RequestException as e:
                print(f"[RETRY {attempt}/{retries}] Offset {offset_val} → {e}")
                time.sleep(delay)

        print(f"[SKIPPED] Offset {offset_val} pominięty po {retries} nieudanych próbach.")
        return []

    while offset < max_offset:
        links = fetch_links(offset)
        if not links:
            break
        all_links.extend(links)
        offset += step

    seen_ids = set()
    unique_links = []
    for link in all_links:
        job_id = link.split("/")[-1]
        if job_id not in seen_ids:
            seen_ids.add(job_id)
            unique_links.append(link)

    print(f"[DEBUG] Unikalnych linków: {len(unique_links)}")

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(extract_tech_stack, link): link for link in unique_links}
        for future in as_completed(futures):
            link = futures[future]
            try:
                stack = future.result()
                offers.append({"url": link, "tech_stack": stack})
            except Exception as e:
                print(f"[STACK ❌] {link}: {e}")

    print(f"[✅] Zebrano {len(offers)} ofert z unikalnym job_id")
    return offers