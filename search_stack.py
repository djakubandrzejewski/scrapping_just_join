import requests
from bs4 import BeautifulSoup
from collections import Counter
import time
from scrapper_offers import get_offer_links

headers = {
    "User-Agent": "Mozilla/5.0"
}

# ← tutaj wklej listę linków które zebrałeś:
offer_urls = get_offer_links()

def extract_tech_stack(url):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    techs = []

    for h4 in soup.find_all("h4"):
        tech = h4.get_text(strip=True)
        level = h4.find_next_sibling("span")
        if level:
            techs.append((tech, level.get_text(strip=True).lower()))
    
    return techs

def main():
    print(f"analyse: {len(offer_urls)} ...")
    tech_counter = Counter()

    for i, url in enumerate(offer_urls):
        print(f"[{i+1}/{len(offer_urls)}] {url}")
        try:
            techs = extract_tech_stack(url)
            for tech, _ in techs:
                tech_counter[tech] += 1
        except Exception as e:
            print(f"error {url}: {e}")
        time.sleep(0.5)  # delikatny throttling

    print("\nNajczęstsze technologie:")
    for tech, count in tech_counter.most_common(30):
        print(f"{tech}: {count}")
