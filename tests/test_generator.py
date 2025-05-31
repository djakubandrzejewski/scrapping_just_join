# tests/test_generator.py

from app.generator import generate_job_offer, generate_custom_offer

def test_generate_job_offer_text():
    techs = ["Python", "Docker"]
    output = generate_job_offer(techs, tag="test")
    assert isinstance(output, str)
    assert "Python" in output or "Docker" in output

def test_generate_custom_offer_text():
    output = generate_custom_offer(
        role="Backend Developer",
        company="TechCorp",
        location="Zdalnie",
        salary="15 000 - 20 000 PLN",
        must_have="Python, Flask",
        nice_to_have="Docker, Kubernetes",
        benefits="Prywatna opieka zdrowotna",
        remote_mode="Zdalna"
    )
    assert isinstance(output, str)
    assert "Backend Developer" in output
    assert "TechCorp" in output