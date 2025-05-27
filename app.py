import streamlit as st
import pandas as pd
from collections import Counter
from generate_job_offer import generate_job_offer
from pdf_utils import save_offer_to_pdf

st.set_page_config(page_title="AI Job Offer Generator", layout="centered")

st.title("AI Generator Job Offer (Data Engineer)")
st.markdown("Load data, select technologies and generate an ad with OpenAI.")

uploaded_file = st.file_uploader("📂 upload file `tech_stack_data.csv`", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    tech_counts = df["Technology"].value_counts()

    st.subheader("most technology")
    st.dataframe(tech_counts.head(10))

    top_5 = tech_counts.head(5).index.tolist()
    rare_5 = tech_counts.tail(5).index.tolist()

    option = st.radio("choose stack:", ["Top 5", "Rare 5", "own choice"])

    if option == "Top 5":
        selected_techs = top_5
    elif option == "Rare 5":
        selected_techs = rare_5
    else:
        selected_techs = st.multiselect("choose technology:", tech_counts.index.tolist(), default=top_5)

    if selected_techs and st.button("generate offfer"):
        with st.spinner("GENERATING OpenAI..."):
            offer_text = generate_job_offer(selected_techs, tag="streamlit")
            st.success("ready")
            st.text_area("📄 generated offer:", offer_text, height=400)

            pdf_buffer = save_offer_to_pdf(offer_text)
            st.download_button(
                    label="save as PDF",
                    data=pdf_buffer,
                    file_name="job_offer.pdf",
                    mime="application/pdf"
            )

