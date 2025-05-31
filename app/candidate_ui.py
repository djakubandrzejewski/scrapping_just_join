# app/candidate_ui.py

import streamlit as st
import pandas as pd
from collections import Counter
from io import StringIO
import altair as alt
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

from app.scrapper import get_offer_links
from app.generator import generate_job_offer
from app.pdf_export import save_offer_to_pdf
from app.categories import CATEGORIES

def show_selected_stack(technologies):
    st.markdown("📦 **Wybrany stack:**")

    # Ustal liczbę kolumn (np. 3)
    num_columns = 3
    cols = st.columns(num_columns)

    for idx, tech in enumerate(technologies):
        col = cols[idx % num_columns]
        col.markdown(f"""
            <div style="background-color:#e7f5ff; border-radius:8px; padding:6px 10px; margin:4px 0; display:inline-block; font-weight:bold;">
                ✅ {tech}
            </div>
        """, unsafe_allow_html=True)

def show_candidate_ui():
    st.subheader("🔎 Wybierz kryteria")
    selected_category = st.selectbox("🎯 Kategoria:", ["Wszystkie"] + list(CATEGORIES.keys()))
    keyword = st.text_input("🔑 Słowo kluczowe", placeholder="np. DevOps, Data Engineer, Python...")

    if "df" not in st.session_state:
        st.session_state.df = None

    if st.button("🔍 Start scrapping"):
        if not keyword.strip():
            st.warning("⚠️ Podaj słowo kluczowe, aby rozpocząć scraping.")
        else:
            category_slug = CATEGORIES.get(selected_category, "all") if selected_category != "Wszystkie" else "all"
            st.info(f"⏳ Rozpoczynam scrapowanie dla: {keyword}")
            with st.spinner("♻️ Scraping w toku..."):
                offer_data = get_offer_links(keyword=keyword.strip(), category=category_slug)

            st.success(f"✅ Zebrano {len(offer_data)} ofert!")

            if not offer_data:
                st.warning("❌ Nie udało się zebrać ofert.")
            else:
                def extract_from_cached(offer):
                    return [(tech, offer["url"]) for tech in offer["tech_stack"]]

                results = [item for offer in offer_data for item in extract_from_cached(offer)]
                tech_counter = Counter([tech for tech, _ in results])
                df = pd.DataFrame(tech_counter.items(), columns=["Technology", "Count"]).sort_values(by="Count", ascending=False)
                st.session_state.df = df

                csv_buffer = StringIO()
                df.to_csv(csv_buffer, index=False)
                st.download_button("⬇️ Pobierz tech_stack_data.csv", data=csv_buffer.getvalue(),
                                   file_name="tech_stack_data.csv", mime="text/csv")

    df = st.session_state.df
    if df is not None:
        tech_counts = df.set_index("Technology")["Count"]
        st.subheader("📊 Najpopularniejsze technologie")
        st.dataframe(tech_counts.head(10))

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

        st.subheader("☁️ WordCloud technologii")
        wc = WordCloud(width=800, height=400, background_color="white")
        wc.generate_from_frequencies(tech_counts)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

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
            show_selected_stack(selected_techs)

            stack_csv_buffer = io.StringIO()
            pd.DataFrame({"Technology": selected_techs}).to_csv(stack_csv_buffer, index=False)
            st.download_button("📥 Pobierz wybrany stack jako CSV", data=stack_csv_buffer.getvalue(),
                               file_name="selected_stack.csv", mime="text/csv")