# tests/test_scrapper.py

from app.scrapper import get_offer_links

def test_get_offer_links_returns_list():
    results = get_offer_links(keyword="Python", category="all")
    assert isinstance(results, list)
    assert len(results) > 0
    assert "url" in results[0]
    assert "tech_stack" in results[0]