"""
StudySpark AI - Main Streamlit Application
"""

import json
import os

import streamlit as st

from workflow import STAGES, create_context, run_stage


# ============================================================
# SAFE HELPERS
# ============================================================

def as_dict(value):
    return value if isinstance(value, dict) else {}


def as_list(value):
    return value if isinstance(value, list) else []


def as_text(value, default=""):
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def display_options(options):
    if isinstance(options, dict):
        for key, value in options.items():
            st.write(f"**{as_text(key)}.** {as_text(value)}")
    elif isinstance(options, list):
        for index, option in enumerate(options):
            st.write(f"**{chr(65 + index)}.** {as_text(option)}")
    elif options:
        st.write(as_text(options))
    else:
        st.caption("No options were returned.")


def display_concepts(concepts):
    items = as_list(concepts)

    if not items:
        st.caption("No key concepts were returned.")
        return

    for item in items:
        if isinstance(item, dict):
            concept = as_text(item.get("concept", ""))
            explanation = as_text(item.get("explanation", ""))

            if concept:
                st.markdown(f"**{concept}**")
            if explanation:
                st.write(explanation)
        else:
            st.write(as_text(item))


def display_flashcards(cards):
    items = as_list(cards)

    if not items:
        st.caption("No flashcards were returned.")
        return

    for index, raw_card in enumerate(items, 1):
        card = as_dict(raw_card)
        question = as_text(card.get("question", f"Card {index}"))
        answer = as_text(card.get("answer", ""))

        with st.expander(f"Card {index}: {question}"):
            st.write(answer or "No answer returned.")


def display_mcqs(mcqs):
    st.markdown("### ❓ MCQs")

    items = as_list(mcqs)

    if not items:
        st.info("No MCQs were returned.")
        return

    for index, raw_mcq in enumerate(items, 1):
        mcq = as_dict(raw_mcq)

        question = as_text(mcq.get("question", ""))
        st.markdown(f"**{index}. {question}**")
