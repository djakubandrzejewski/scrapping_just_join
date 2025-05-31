import streamlit as st
from app.generator import generate_custom_offer
from app.pdf_export import save_offer_to_pdf

def display_job_offer(offer_text: str):
    st.markdown("### 📄 Podgląd ogłoszenia")

    with st.container():
        st.markdown("---")
        st.markdown(offer_text)  # natywne renderowanie markdown
        st.markdown("---")

def show_recruiter_ui():
    st.title("🧑‍💼 Kreator ogłoszenia rekrutacyjnego")

    with st.form("job_form"):
        st.markdown("### 📝 Podstawowe informacje")
        role = st.text_input("📌 Stanowisko", placeholder="Np. Frontend Developer")
        company = st.text_input("🏢 Firma", placeholder="Np. Software House X")
        location = st.text_input("🌍 Lokalizacja", placeholder="Np. Zdalnie / Warszawa")
        salary = st.text_input("💸 Widełki wynagrodzenia", placeholder="Np. 12 000 - 18 000 PLN B2B")

        st.markdown("### 🎯 Wymagania")
        must_have = st.text_area("✅ Must-have (wymagane)", height=100)
        nice_to_have = st.text_area("✨ Nice-to-have (mile widziane)", height=80)

        st.markdown("### 🎁 Benefity")
        benefits = st.text_area("🎉 Co oferujecie kandydatom?", height=100)
        remote = st.radio("🏠 Tryb pracy", ["Zdalna", "Hybrydowa", "Stacjonarna"])

        submitted = st.form_submit_button("✏️ Wygeneruj ogłoszenie")

    if submitted:
        if not role or not company:
            st.error("❌ Proszę uzupełnić pola: stanowisko i nazwa firmy.")
            return

        with st.spinner("🧠 Generuję ogłoszenie..."):
            offer_text = generate_custom_offer(
                role=role,
                company=company,
                location=location,
                salary=salary,
                must_have=must_have,
                nice_to_have=nice_to_have,
                benefits=benefits,
                remote_mode=remote
            )

        st.success("✅ Ogłoszenie zostało wygenerowane!")
        display_job_offer(offer_text)

        pdf = save_offer_to_pdf(offer_text)
        st.download_button("💾 Pobierz jako PDF", data=pdf, file_name="job_offer.pdf", mime="application/pdf")

        markdown_buffer = offer_text.encode("utf-8")
        st.download_button(
            "📥 Pobierz jako Markdown",
            data=markdown_buffer,
            file_name="job_offer.md",
            mime="text/markdown"
        )