import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.114 Safari/537.36"
    )
}

BASE_URL = "https://justjoin.it"

def extract_tech_stack(offer_url: str) -> list[str]:
    try:
        response = requests.get(offer_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        stack_elements = soup.select("div.MuiBox-root h4.MuiTypography-root.MuiTypography-subtitle2")
        stack = [el.get_text(strip=True) for el in stack_elements if el.get_text(strip=True)]

        if not stack:
            print(f"[STACK] ⚠️ Brak stacka w {offer_url}")
        else:
            print(f"[STACK] ✅ Stack w {offer_url}: {stack}")

        return stack
    except Exception as e:
        print(f"[STACK] ❌ Błąd podczas scrapowania {offer_url} → {e}")
        return []

def get_offer_links(keyword: str = "", category: str = "all") -> List[Dict[str, str]]:
    offers = []
    seen_links = set()
    offset = 0
    executor = ThreadPoolExecutor(max_workers=10)
    fine_scan_mode = False
    fine_offset = None
    empty_hits = 0
    max_empty = 5

    while True:
        url = f"{BASE_URL}/job-offers/all-locations"
        if category and category != "all":
            url += f"/{quote(category)}"

        params = {"keyword": keyword, "from": offset}
        param_str = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
        full_url = f"{url}?{param_str}"

        print(f"[DEBUG] Scraping: {full_url} | Offset: {offset} | Mode: {'fine' if fine_scan_mode else 'bulk'}")
        try:
            res = requests.get(full_url, headers=HEADERS, timeout=10)
            res.raise_for_status()
        except Exception as e:
            print(f"[❌] Błąd pobierania strony: {e}")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("/job-offer/") and "?" not in a["href"]]
        full_links = [BASE_URL + l for l in links]
        unique_links = [l for l in full_links if l not in seen_links]

        print(f"[DEBUG] Nowych ofert: {len(unique_links)}")

        if not unique_links:
            empty_hits += 1
            if fine_scan_mode and empty_hits >= max_empty:
                print("[STOP] Fine scan zakończony – brak nowych wyników.")
                break
        else:
            empty_hits = 0

        futures = {executor.submit(extract_tech_stack, link): link for link in unique_links}

        for future in as_completed(futures):
            link = futures[future]
            try:
                stack = future.result()
                offers.append({"url": link, "tech_stack": stack})
                seen_links.add(link)
            except Exception as e:
                print(f"[STACK] ❌ Błąd stacka w {link}: {e}")

        # Tryb bulk: offset += 100, przechodzimy do fine-scan gdy jest mniej niż 100 linków
        if not fine_scan_mode:
            if len(unique_links) < 100:
                fine_scan_mode = True
                fine_offset = offset + 1
                offset = fine_offset
            else:
                offset += 100
        else:
            offset += 1

    executor.shutdown(wait=True)
    return offers
