import streamlit as st

from app.navigation import sidebar
from app.theme import load_theme

st.set_page_config(
    page_title="LifeOS",
    page_icon="🚀",
    layout="wide",
)

load_theme()

page = sidebar()

if page == "dashboard":
    st.title("🏠 Dashboard")
    st.info("Coming soon...")

elif page == "study":
    st.switch_page("pages/01_Study.py")

else:
    st.title(page.title())
    st.info("Coming soon...")