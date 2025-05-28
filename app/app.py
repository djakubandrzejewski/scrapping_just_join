import streamlit as st
import pandas as pd
from collections import Counter
from io import StringIO
import altair as alt
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

from scrapper import get_offer_links
from generator import generate_job_offer
from pdf_export import save_offer_to_pdf
from categories import CATEGORIES

st.set_page_config(page_title="AI Job Offer Generator", layout="centered")
st.title("💼 AI Generator Job Offer (Data Engineer)")
st.markdown("Wybierz źródło danych, wygeneruj ogłoszenie z pomocą OpenAI 🚀")

# --- WYBÓR ŹRÓDŁA DANYCH ---
st.subheader("📥 Wybierz źródło danych")
data_source = st.radio("Źródło danych:", ["Scrappuj z JustJoin", "Wgraj własny plik CSV"])
selected_category = st.selectbox(
    "🎯 Wybierz kategorię (opcjonalnie):",
    options=["Wszystkie"] + list(CATEGORIES.keys())
)

# Inicjalizacja sesji
if "df" not in st.session_state:
    st.session_state.df = None

# --- SCRAPPING ---
if data_source == "Scrappuj z JustJoin":
    keyword = st.text_input("🔑 Podaj słowo kluczowe", value="data engineer", key="keyword_input")

    if st.button("🔍 Start scrapping"):
        st.info(f"⏳ Scrapping dla słowa: {keyword}")

        category_slug = None if selected_category == "Wszystkie" else CATEGORIES[selected_category]
        category_slug = category_slug or "all"
        keyword = keyword.strip() if keyword else ""

        offer_data = get_offer_links(keyword=keyword, category=category_slug)

        st.success(f"✅ Znaleziono {len(offer_data)} ofert!")

        def extract_from_cached(offer):
            return [(tech, offer["url"]) for tech in offer["tech_stack"]]

        results = []
        progress = st.progress(0)
        status = st.empty()

        for i, offer in enumerate(offer_data):
            results.extend(extract_from_cached(offer))
            status.write(f"🔗 [{i+1}/{len(offer_data)}] {offer['url']}")
            progress.progress((i + 1) / len(offer_data))

        if not results:
            st.warning("❌ Nie udało się zebrać danych.")
        else:
            tech_counter = Counter([tech for tech, _ in results])
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