# app/recruiter_ui.py

import streamlit as st
from app.generator import generate_job_offer
from app.pdf_export import save_offer_to_pdf

def show_recruiter_ui():
    st.header("🧠 Generator ogłoszenia (Rekruter)")

    st.markdown("✍️ Wpisz wymagania i szczegóły stanowiska (język naturalny):")
    prompt = st.text_area("Opis stanowiska", height=200,
                          placeholder="Np. Szukam senior backend developera z Laravel + PostgreSQL. Zdalnie, B2B, minimum 3 lata doświadczenia.")

    if st.button("🚀 Wygeneruj ogłoszenie"):
        if not prompt.strip():
            st.warning("⚠️ Najpierw wpisz treść.")
        else:
            with st.spinner("Generuję treść ogłoszenia..."):
                offer = generate_job_offer(prompt, tag="recruiter_freeform")
                st.success("✅ Ogłoszenie gotowe!")
                st.text_area("📄 Ogłoszenie:", offer, height=400)

                pdf = save_offer_to_pdf(offer)
                st.download_button("💾 Pobierz PDF", data=pdf, file_name="job_offer.pdf", mime="application/pdf")