import streamlit as st


PAGES = {
    "🏠 Dashboard": "dashboard",
    "📚 Study": "study",
    "💪 Gym": "gym",
    "🍽 Nutrition": "nutrition",
    "❤️ Health": "health",
    "⌨ Typing": "typing",
    "📊 Analytics": "analytics",
    "⚙ Settings": "settings",
}


def sidebar():
    st.sidebar.title("🚀 LifeOS")

    page = st.sidebar.radio(
        "Navigation",
        list(PAGES.keys()),
    )

    return PAGES[page]