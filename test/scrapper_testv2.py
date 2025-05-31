import requests

def get_offers():
    url = "https://justjoin.it/api/offers"
    response = requests.get(url)
    if response.status_code == 200:
        offers = response.json()
        for offer in offers:
            print(f"Title: {offer['title']}, Company: {offer['company_name']}, City: {offer['city']}")
    else:
        print(f"Failed to retrieve offers. Status code: {response.status_code}")

get_offers()