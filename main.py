from scrapper_offers import get_offer_links      
from search_stack import extract_tech_stack       
from collections import Counter
import time

def main():
    # 1. Pobierz linki
    offer_urls = get_offer_links()               
    print(f"Znaleziono {len(offer_urls)} ofert.\n")

    # 2. Liczenie technologii
    tech_counter = Counter()

    for i, url in enumerate(offer_urls):
        print(f"[{i+1}/{len(offer_urls)}] {url}")
        try:
            techs = extract_tech_stack(url)      
            for tech, _ in techs:
                tech_counter[tech] += 1
        except Exception as e:
            print(f"error {url}: {e}")
        time.sleep(0.5)

    # 3. Wynik
    print("\n technologies used:")
    for tech, count in tech_counter.most_common(30):
        print(f"{tech}: {count}")

if __name__ == "__main__":
    main()
