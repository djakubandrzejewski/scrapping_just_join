import streamlit as st
import pandas as pd
from collections import Counter
from io import StringIO
import altair as alt
import io

from app.scrapper import get_offer_links
from app.learning_ui import show_learning_ui
from app.categories import CATEGORIES

# Pomocnicza funkcja do ładnego wyświetlania technologii
def show_selected_stack(technologies):
    st.markdown("📦 **Wybrany stack:**")
    cols = st.columns(3)
    for i, tech in enumerate(technologies):
        with cols[i % 3]:
            st.markdown(
                f"""<div style="background-color:#e7f5ff; border-radius:6px; padding:6px 10px; margin:4px 0; display:inline-block; font-weight:500;">
                ✅ {tech}
                </div>""",
                unsafe_allow_html=True
            )

def show_candidate_ui():
    st.subheader("🔎 Wybierz kryteria")
    selected_category = st.selectbox("🎯 Kategoria:", ["Wszystkie"] + list(CATEGORIES.keys()))
    keyword = st.text_input("🔑 Słowo kluczowe", placeholder="np. DevOps, Data Engineer, Python...")

    if "df" not in st.session_state:
        st.session_state.df = None
    if "offers" not in st.session_state:
        st.session_state.offers = None

    if st.button("🔍 Start scrapping"):
        if not keyword.strip():
            st.warning("⚠️ Podaj słowo kluczowe, aby rozpocząć scraping.")
        else:
            category_slug = CATEGORIES.get(selected_category, "all") if selected_category != "Wszystkie" else "all"
            st.info(f"⏳ Rozpoczynam scrapowanie dla: `{keyword}`...")
            with st.spinner("♻️ Scraping w toku..."):
                offer_data = get_offer_links(keyword=keyword.strip(), category=category_slug)

            st.success(f"✅ Zebrano {len(offer_data)} ofert.")
            st.session_state.offers = offer_data

            if not offer_data:
                st.warning("❌ Nie udało się zebrać ofert.")
                return

            # Zlicz technologię
            results = [(tech, offer["url"]) for offer in offer_data for tech in offer["tech_stack"]]
            tech_counter = Counter([tech for tech, _ in results])
            df = pd.DataFrame(tech_counter.items(), columns=["Technology", "Count"]).sort_values(by="Count", ascending=False)
            st.session_state.df = df

            # Export CSV
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button("⬇️ Pobierz tech_stack_data.csv", data=csv_buffer.getvalue(),
                               file_name="tech_stack_data.csv", mime="text/csv")

    # Po scrappingu
    df = st.session_state.df
    if df is not None:
        st.subheader("📊 Najpopularniejsze technologie")
        tech_counts = df.set_index("Technology")["Count"]
        st.dataframe(tech_counts.head(10))

        # Wykres
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
            show_selected_stack(selected_techs)

            # Pobierz jako CSV
            stack_csv_buffer = io.StringIO()
            pd.DataFrame({"Technology": selected_techs}).to_csv(stack_csv_buffer, index=False)
            st.download_button("📥 Pobierz wybrany stack jako CSV", data=stack_csv_buffer.getvalue(),
                               file_name="selected_stack.csv", mime="text/csv")

            # Co chcesz dalej?
            st.markdown("---")
            st.subheader("🤔 Co chcesz zrobić dalej?")

            st.markdown("""
            <div style="font-size:16px; line-height:1.6; background-color:#f0f2f6; padding:15px 20px; border-radius:10px; margin-bottom:20px;">
            Na podstawie wybranych technologii możesz wybrać swoją dalszą ścieżkę:
            <ul>
                <li><strong>📚 Rozwój:</strong> Jeśli chcesz pogłębiać wiedzę i dostać rekomendacje kursów, artykułów i zasobów.</li>
                <li><strong>✉️ Aplikacja:</strong> Jeśli jesteś gotowy aplikować na oferty pasujące do Twojego stacku.</li>
            </ul>
            Wybierz poniżej preferowaną opcję:
            </div>
            """, unsafe_allow_html=True)

            next_action = st.radio("🎯 Wybierz moduł:", ["📚 Chcę się rozwijać", "✉️ Chcę aplikować na oferty"], horizontal=True)

            if next_action == "📚 Chcę się rozwijać":
                if st.button("🧠 Przejdź do nauki"):
                    st.session_state.selected_techs = selected_techs
                    st.session_state.page = "learning"
                    return

            elif next_action == "✉️ Chcę aplikować na oferty":
                st.info("🚧 Moduł aplikowania zostanie dodany w kolejnych krokach.")