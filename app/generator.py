import openai
import os
from dotenv import load_dotenv

# Załaduj dane z .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_job_offer(technologies: list, tag: str = "default") -> str:
    """
    Tworzy ogłoszenie o pracę dla stanowiska Data Engineer na podstawie technologii.
    technologies: lista technologii [str]
    tag: do ewentualnego zapisu pliku
    """
    tech_list = ", ".join(technologies)
    prompt = (
        f"Stwórz profesjonalne ogłoszenie o pracę na stanowisko Data Engineer. "
        f"Wymagane technologie to: {tech_list}. "
        "Ogłoszenie powinno zawierać opis firmy, obowiązki, wymagania, benefity i zakończenie w stylu zachęty do aplikacji."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem HR i copywriterem IT."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        content = response.choices[0].message["content"]

        filename = f"generated_offer_{tag}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"saved: {filename}")
        return content

    except Exception as e:
        print(f"error: {e}")
        return "error."
