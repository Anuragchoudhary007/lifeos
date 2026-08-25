from __future__ import annotations

import streamlit as st


def section(title: str) -> None:
    st.markdown(f"## {title}")