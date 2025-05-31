# tests/test_stack_extractor.py

from app.search import extract_tech_stack

def test_extract_tech_stack_structure():
    sample_url = "https://justjoin.it/job-offer/example-link"  # lub prawdziwy testowy link
    stack = extract_tech_stack(sample_url)
    assert isinstance(stack, list)