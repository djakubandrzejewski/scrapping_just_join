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

from scrapper_offers import get_offer_links
from search_stack import extract_tech_stack
from generate_job_offer import generate_job_offer
from pdf_utils import save_offer_to_pdf

st.set_page_config(page_title="AI Job Offer Generator", layout="centered")
st.title("💼 AI Generator Job Offer (Data Engineer)")
st.markdown("Wybierz źródło danych, wygeneruj ogłoszenie z pomocą OpenAI 🚀")

# --- WYBÓR ŹRÓDŁA DANYCH ---
st.subheader("📥 Wybierz źródło danych")
data_source = st.radio("Skąd chcesz pobrać dane?", ["Scrappuj z JustJoin", "Wgraj własny plik CSV"])

df = None  # docelowy DataFrame

# --- SCRAPPING Z JUSTJOIN ---
keyword = st.text_input("🔑 Podaj słowo kluczowe (np. 'python', 'react', 'data engineer')", value="data engineer")

if st.button("🔍 Start scrapping"):
        st.info(f"⏳ Scrapping dla keyword: **{keyword}**")
        offer_urls = get_offer_links(keyword)
        st.info("⏳ Scrapping in progress...")
        offer_urls = get_offer_links()
        st.success(f"✅ Found {len(offer_urls)} offers!")

        tech_counter = Counter()
        progress = st.progress(0)
        status = st.empty()

        for i, url in enumerate(offer_urls):
            status.write(f"🔗 [{i+1}/{len(offer_urls)}] {url}")
            try:
                techs = extract_tech_stack(url)
                for tech, _ in techs:
                    tech_counter[tech] += 1
            except Exception as e:
                st.error(f"Błąd: {e}")
            progress.progress((i + 1) / len(offer_urls))
            time.sleep(0.2)

        df = pd.DataFrame(tech_counter.items(), columns=["Technology", "Count"]).sort_values(by="Count", ascending=False)
        df.to_csv("tech_stack_data.csv", index=False)

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="⬇️ Download scraped tech_stack_data.csv",
            data=csv_buffer.getvalue(),
            file_name="tech_stack_data.csv",
            mime="text/csv"
        )
        st.success("📥 Zapisano jako tech_stack_data.csv")

# --- WGRYWANIE WŁASNEGO CSV ---
elif data_source == "Wgraj własny plik CSV":
    uploaded_file = st.file_uploader("📂 Upload `tech_stack_data.csv`", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)

# --- OBSŁUGA DANYCH ---
if df is not None:
    tech_counts = df.set_index("Technology")["Count"]
    st.subheader("📊 Najpopularniejsze technologie")
    st.dataframe(tech_counts.head(10))

    # WYKRES SŁUPKOWY
    chart_df = tech_counts.head(10).reset_index()
    chart_df.columns = ["Technology", "Count"]

    st.subheader("📈 Wykres słupkowy: Top 10 technologii")
    bar_chart = alt.Chart(chart_df).mark_bar().encode(
        x=alt.X("Count:Q", title="Liczba wystąpień"),
        y=alt.Y("Technology:N", sort="-x", title="Technologia"),
        tooltip=["Technology", "Count"]
    ).properties(width=600, height=400)

    st.altair_chart(bar_chart, use_container_width=True)

    # WORDCLOUD
    st.subheader("☁️ WordCloud technologii")
    wc = WordCloud(width=800, height=400, background_color='white')
    wc.generate_from_frequencies(tech_counts)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # WYBÓR STACKU
    top_5 = tech_counts.head(5).index.tolist()
    rare_5 = tech_counts.tail(5).index.tolist()

    st.subheader("🧱 Wybierz technologię do oferty")
    option = st.radio("🎯 Stack:", ["Top 5", "Rare 5", "Własny wybór"])

    if option == "Top 5":
        selected_techs = top_5
    elif option == "Rare 5":
        selected_techs = rare_5
    else:
        selected_techs = st.multiselect("🔧 Wybierz technologie:", tech_counts.index.tolist(), default=top_5)

    # 👉 Eksport przed generowaniem
    if selected_techs:
        st.write("📦 Wybrany stack:", selected_techs)
        stack_csv_buffer = io.StringIO()
        pd.DataFrame({"Technology": selected_techs}).to_csv(stack_csv_buffer, index=False)

        st.download_button(
            label="📥 Pobierz wybrany stack jako CSV",
            data=stack_csv_buffer.getvalue(),
            file_name="selected_stack.csv",
            mime="text/csv"
        )

    # GENEROWANIE OGŁOSZENIA
    if selected_techs and st.button("📝 Wygeneruj ogłoszenie"):
        with st.spinner("🧠 Generuję z pomocą OpenAI..."):
            offer_text = generate_job_offer(selected_techs, tag="streamlit")
            st.success("✅ Gotowe ogłoszenie!")
            st.text_area("📄 Generated offer:", offer_text, height=400)

            pdf_buffer = save_offer_to_pdf(offer_text)
            st.download_button(
                label="💾 Pobierz jako PDF",
                data=pdf_buffer,
                file_name="job_offer.pdf",
                mime="application/pdf"
            )