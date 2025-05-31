import openai
import os
from dotenv import load_dotenv

# Załaduj dane z .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_job_offer(prompt_input, tag: str = "default") -> str:
    """
    Generuje ogłoszenie o pracę na podstawie:
    - listy technologii (dla kandydatów)
    - lub swobodnego prompta (dla rekruterów)

    prompt_input: list[str] lub str
    tag: służy do zapisania do pliku
    """
    if isinstance(prompt_input, list):
        tech_list = ", ".join(prompt_input)
        prompt = (
            f"Stwórz profesjonalne ogłoszenie o pracę na stanowisko Data Engineer. "
            f"Wymagane technologie to: {tech_list}. "
            "Ogłoszenie powinno zawierać opis firmy, obowiązki, wymagania, benefity "
            "i zakończenie w stylu zachęty do aplikacji."
        )
    elif isinstance(prompt_input, str):
        prompt = (
            f"Na podstawie poniższego opisu, stwórz profesjonalne ogłoszenie o pracę:\n\n{prompt_input.strip()}"
        )
    else:
        return "❌ Nieprawidłowy format danych wejściowych."

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

        print(f"[Zapisano]: {filename}")
        return content

    except Exception as e:
        print(f"[Błąd generowania]: {e}")
        return "❌ Błąd podczas generowania ogłoszenia."