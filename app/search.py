import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0"
}

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