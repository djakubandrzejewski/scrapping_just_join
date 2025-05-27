import streamlit as st
import os
import pandas as pd
from collections import Counter
import time
from io import StringIO
import altair as alt
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

from scrapper import get_offer_links
from search import extract_tech_stack
from generator import generate_job_offer
from pdf_export import save_offer_to_pdf
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="AI Job Offer Generator", layout="centered")
st.title("💼 AI Generator Job Offer (Data Engineer)")
st.markdown("Wybierz źródło danych, wygeneruj ogłoszenie z pomocą OpenAI 🚀")

# --- WYBÓR ŹRÓDŁA DANYCH ---
st.subheader("📥 Wybierz źródło danych")
data_source = st.radio("Źródło danych:", ["Scrappuj z JustJoin", "Wgraj własny plik CSV"])

# Inicjalizacja sesji
if "df" not in st.session_state:
    st.session_state.df = None

# --- SCRAPPING ---
if data_source == "Scrappuj z JustJoin":
    keyword = st.text_input("🔑 Podaj słowo kluczowe", value="data engineer", key="keyword_input")

    if st.button("🔍 Start scrapping"):
        st.info(f"⏳ Scrapping dla słowa: {keyword}")
        offer_urls = get_offer_links(keyword)
        st.success(f"✅ Znaleziono {len(offer_urls)} ofert!")

        def scrape_single(url):
            try:
                techs = extract_tech_stack(url)
                return [(tech, level, url) for tech, level in techs]
            except Exception:
                return []

        results = []
        progress = st.progress(0)
        status = st.empty()

        with ThreadPoolExecutor(max_workers=10) as executor:
            for i, res in enumerate(executor.map(scrape_single, offer_urls)):
                results.extend(res)
                status.write(f"🔗 [{i+1}/{len(offer_urls)}] {offer_urls[i]}")
                progress.progress((i + 1) / len(offer_urls))

        if not results:
            st.warning("❌ Nie udało się zebrać danych.")
        else:
            tech_counter = Counter([tech for tech, _, _ in results])
            df = pd.DataFrame(tech_counter.items(), columns=["Technology", "Count"]).sort_values(by="Count", ascending=False)
            st.session_state.df = df

            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button("⬇️ Pobierz tech_stack_data.csv", data=csv_buffer.getvalue(),
                               file_name="tech_stack_data.csv", mime="text/csv")

# --- UPLOAD CSV ---
elif data_source == "Wgraj własny plik CSV":
    uploaded_file = st.file_uploader("📂 Załaduj CSV", type="csv")
    if uploaded_file:
        st.session_state.df = pd.read_csv(uploaded_file)

# --- OBSŁUGA DANYCH ---
df = st.session_state.df
if df is not None:
    tech_counts = df.set_index("Technology")["Count"]
    st.subheader("📊 Najpopularniejsze technologie")
    st.dataframe(tech_counts.head(10))

    # Wykres słupkowy
    chart_df = tech_counts.head(10).reset_index()
    chart_df.columns = ["Technology", "Count"]
    st.subheader("📈 Wykres słupkowy: Top 10 technologii")
    st.altair_chart(
        alt.Chart(chart_df).mark_bar().encode(
            x="Count:Q",
            y=alt.Y("Technology:N", sort="-x"),
            tooltip=["Technology", "Count"]
        ).properties(width=600, height=400),
        use_container_width=True
    )

    # WordCloud
    st.subheader("☁️ WordCloud technologii")
    wc = WordCloud(width=800, height=400, background_color="white")
    wc.generate_from_frequencies(tech_counts)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # Wybór technologii
    top_5 = tech_counts.head(5).index.tolist()
    rare_5 = tech_counts.tail(5).index.tolist()
    option = st.radio("🎯 Wybierz stack:", ["Top 5", "Rare 5", "Własny wybór"])

    if option == "Top 5":
        selected_techs = top_5
    elif option == "Rare 5":
        selected_techs = rare_5
    else:
        selected_techs = st.multiselect("🔧 Wybierz technologie:", tech_counts.index.tolist(), default=top_5)

    if selected_techs:
        st.write("📦 Wybrany stack:", selected_techs)

        # Eksport stacka
        stack_csv_buffer = io.StringIO()
        pd.DataFrame({"Technology": selected_techs}).to_csv(stack_csv_buffer, index=False)
        st.download_button("📥 Pobierz wybrany stack jako CSV", data=stack_csv_buffer.getvalue(),
                           file_name="selected_stack.csv", mime="text/csv")

        # Generowanie ogłoszenia
        if st.button("📝 Wygeneruj ogłoszenie"):
            with st.spinner("🧠 Generuję ogłoszenie..."):
                offer_text = generate_job_offer(selected_techs, tag="streamlit")
                st.success("✅ Gotowe ogłoszenie!")
                st.text_area("📄 Wygenerowana treść:", offer_text, height=400)

                pdf_buffer = save_offer_to_pdf(offer_text)
                st.download_button("💾 Pobierz jako PDF", data=pdf_buffer,
                                   file_name="job_offer.pdf", mime="application/pdf")