from pathlib import Path

import streamlit as st


def load_theme() -> None:
    css_path = Path(__file__).parent / "styles" / "global.css"

    with open(css_path, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )