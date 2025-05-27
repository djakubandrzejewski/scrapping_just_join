from scrapper_offers import get_offer_links
from search_stack import extract_tech_stack
from export_results import export_full_tech_data
from generate_job_offer import generate_job_offer
from collections import Counter
import time

def main():
    offer_urls = get_offer_links()
    print(f"Znaleziono {len(offer_urls)} ofert.\n")

    tech_counter = Counter()
    all_tech_data = []

    for i, url in enumerate(offer_urls):
        print(f"[{i+1}/{len(offer_urls)}] {url}")
        try:
            techs = extract_tech_stack(url)
            for tech, level in techs:
                tech_counter[tech] += 1
                all_tech_data.append((tech, level, url))
        except Exception as e:
            print(f"❌ Błąd przy {url}: {e}")
        time.sleep(0.5)

    print("\n📊 Najczęstsze technologie:")
    for tech, count in tech_counter.most_common(30):
        print(f"{tech}: {count}")

    export_full_tech_data(all_tech_data)

    # 🔝 i 🔻 tech stacki
    top_5 = [tech for tech, _ in tech_counter.most_common(5)]
    rare_5 = [tech for tech, _ in tech_counter.most_common()[-5:]]

    print("\n🧠 Generuję ogłoszenie dla najpopularniejszych technologii...")
    generate_job_offer(top_5, tag="top5")

    print("\n🧠 Generuję ogłoszenie dla najrzadszych technologii...")
    generate_job_offer(rare_5, tag="rare5")

if __name__ == "__main__":
    main()