import streamlit as st
from app.generator import get_technology_summary

def show_learning_ui(all_techs):
    st.title("🧠 Sekcja rozwoju")

    if st.button("⬅️ Wróć do ofert"):
        st.session_state.page = "candidate"
        st.rerun()

    if not all_techs:
        st.warning("⚠️ Brak wybranego stacku. Wróć i wybierz technologie.")
        return

    st.markdown("## 🔍 Wybierz technologie, z których chcesz się rozwijać")
    selected_to_learn = st.multiselect(
        "🔧 Technologie do nauki:",
        all_techs,
        default=all_techs[:3]
    )

    if selected_to_learn:
        if st.button("📘 Wygeneruj rekomendacje"):
            st.session_state.learning_results = {}
            for tech in selected_to_learn:
                with st.spinner(f"🔄 Generuję opis i zasoby dla: {tech}"):
                    st.session_state.learning_results[tech] = get_technology_summary(tech)
            st.success("✅ Gotowe!")

    if "learning_results" in st.session_state and st.session_state.learning_results:
        st.markdown("---")
        st.subheader("📚 Twoje rekomendacje do nauki")

        for tech, summary in st.session_state.learning_results.items():
            with st.expander(f"📘 {tech}"):
                st.markdown(summary)

                st.markdown("**🔗 Polecane materiały:**")
                st.markdown(f"""
                - [📺 Kursy na Udemy](https://www.udemy.com/courses/search/?q={tech})
                - [📘 Dokumentacja {tech}](https://devdocs.io)
                - [📖 Artykuły na Medium](https://medium.com/search?q={tech})
                """)

    else:
        st.info("ℹ️ Wybierz technologie i kliknij przycisk powyżej, aby wygenerować rekomendacje.")
