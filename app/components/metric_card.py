from __future__ import annotations

import streamlit as st


def metric_card(
    title: str,
    value: str,
    delta: str | None = None,
) -> None:
    """Display a styled metric card."""

    with st.container(border=True):
        st.metric(
            label=title,
            value=value,
            delta=delta,
        )