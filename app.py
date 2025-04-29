import os
import time
import warnings
from typing import Literal
import fitz
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.types import Command
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
from fpdf import FPDF
import base64
import streamlit as st
from langgraph.graph import MessagesState
from backend import run_chatbot

def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
    except Exception as e:
        st.warning(f"Error reading PDF: {e}")
    return text

# Set wide layout
st.set_page_config(layout="wide")
st.title("🧠 Campaign BOT")

# Two-column layout
left_col, right_col = st.columns([2, 3])

with left_col:
    st.header("Campaign Details")
    product_name = st.text_input("Product Name", placeholder="EcoSmart Watch")
    product_description = st.text_area("Product Description", height=100, placeholder="Luxury sustainable smartwatch")
    target_audience = st.text_input("Target Audience", placeholder="Engineering students")
    place = st.text_input("Place/Region", placeholder="India")
    budget = st.number_input("Campaign Budget ($)", min_value=1000, max_value=1_000_000_000, step=500, value=5000)

    uploaded_pdf = st.file_uploader("📎 Optional: Attach a brief or spec PDF", type="pdf")
    # Validate required fields
    fields_filled = all([
        product_name.strip(),
        product_description.strip(),
        target_audience.strip(),
        place.strip(),
        budget > 0
    ])

    generate = st.button("Generate Campaign", disabled=not fields_filled)

    if not fields_filled:
        st.warning("⚠️ Please fill all required fields to enable the campaign generator.")

with right_col:
    st.header("📈 Response")
    with st.expander("Campaign Output", expanded=True):
        if generate:
            pdf_text = ""
            if uploaded_pdf:
                pdf_text = extract_text_from_pdf(uploaded_pdf)

            campaign_request = (
                f"Create a marketing campaign for a {product_name}.\n"
                f"Description: {product_description}\n"
                f"Target Audience: {target_audience}\n"
                f"Location: {place}\n"
                f"Budget: ${budget}\n"
            )
            if pdf_text.strip():
                campaign_request += f"\nAdditional Information from PDF:\n{pdf_text.strip()}"

            transcript, final_answer = run_chatbot(campaign_request)

            st.subheader("Final Campaign Proposal:")
            st.write(final_answer if final_answer else "No final answer was generated.")
        else:
            st.info("Enter the campaign details on the left and click the button.")
