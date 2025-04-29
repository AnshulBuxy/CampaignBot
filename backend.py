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

from io import BytesIO

# Load environment variables
load_dotenv()
warnings.simplefilter("ignore")

# Load Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0,
    timeout=None,
    max_retries=2,
)

# Import tools
from campaign_tools_corrected import (
    content_writer_tools,
    graphic_designer_tools,
    data_analyst_tools,
    brand_manager_tools,
)

# Agent identity enforcement
def get_next_node(last_message, goto, role):
    if "FINAL ANSWER" in last_message.content:
        return END if role == "brand_manager" else goto
    return goto

# Prompt builder
def make_system_prompt(role_desc: str) -> str:
    return (
        "You are a helpful AI assistant collaborating with other assistants. "
        "Use your expertise to advance the campaign design. "
        "If you or any colleague have the final campaign proposal, prefix your response with FINAL ANSWER so the team stops."
        f"\nRole instructions: {role_desc}"
    )

# Agent definitions
content_writer_agent = create_react_agent(
    llm,
    tools=content_writer_tools,
    prompt=make_system_prompt(
        "You are the Content Writer. Analyze the product and audience. "
        "Generate creative ideas for slogans, tone, and copy.\nYou have access to two helpful tools: RewriteTone and CopyInspo. "
        "Do NOT plan the full campaign."
    ),
)

def content_writer_node(state: MessagesState) -> Command[Literal["graphic_designer", END]]:
    result = content_writer_agent.invoke(state)
    result["messages"][-1] = HumanMessage(content=result["messages"][-1].content, name="ContentWriter")
    return Command(update={"messages": state["messages"] + result["messages"]}, goto=get_next_node(result["messages"][-1], "graphic_designer", "content_writer"))

graphic_designer_agent = create_react_agent(
    llm,
    tools=graphic_designer_tools,
    prompt=make_system_prompt(
        "You are the Graphic Designer. Propose visual themes, color schemes, and layout ideas for the campaign. "
        "If you disagree with a proposal (e.g., you prefer a minimalist look), state your reasoning."
        "\n\nYou can use two tools:"
        "\n- 🎨 PaletteGenerator: Generate color palettes for the campaign." \
        "\n- 🔤 FontSuggester: Suggest fonts that match the campaign theme."
    ),
)

def graphic_designer_node(state: MessagesState) -> Command[Literal["data_analyst", END]]:
    result = graphic_designer_agent.invoke(state)
    result["messages"][-1] = HumanMessage(content=result["messages"][-1].content, name="GraphicDesigner")
    return Command(update={"messages": state["messages"] + result["messages"]}, goto=get_next_node(result["messages"][-1], "data_analyst", "graphic_designer"))

data_analyst_agent = create_react_agent(
    llm,
    tools=data_analyst_tools,
    prompt=make_system_prompt(
        "You are the Data Analyst. Validate the marketing campaign using real-world data."
        "\n\nYou can use two tools:"
        "\n- 📈 TrendData: Analyze keyword popularity using Google Trends."
        "\n- 🔍 DataSearch: Find latest news, reports, blogs, or customer insights."
        "\n\nInstructions:"
        "\n- Use data to validate whether the proposed campaign matches customer interest."
        "\n- If the campaign idea seems weak based on data, suggest improvements politely."
        "\n- Only provide factual validation or corrections. Do NOT rewrite or replan the entire campaign."
        "\n\nPass your findings to the Brand Manager after validation."
    ),
)

def data_analyst_node(state: MessagesState) -> Command[Literal["brand_manager", END]]:
    result = data_analyst_agent.invoke(state)
    result["messages"][-1] = HumanMessage(content=result["messages"][-1].content, name="DataAnalyst")
    return Command(update={"messages": state["messages"] + result["messages"]}, goto=get_next_node(result["messages"][-1], "brand_manager", "data_analyst"))

brand_manager_agent = create_react_agent(
    llm,
    tools=brand_manager_tools,
    prompt=make_system_prompt(
        "You are the Brand Manager. You must evaluate and finalize the campaign. "
        "Structure your FINAL ANSWER with these sections:\n"
        "- 📝 Campaign Name\n"
        "- 📜 Executive Summary:\n"
        "- 🎯 Target Audience\n"
        "- 📈 Strategy\n"
        "- 📸 Content Plan\n"
        "- 📣 Creative Execution(include visual theme and color scheme)"
        "- 💰 Budget\n"
        "- ✍️ Key Messages\n"
        "- 🤝 Influencers\n"
        "- 📅 Timeline\n"
        "- 🧠 Creative Concepts\n"
        "- 📍 Landing Page\n"
        "- 📊 KPIs\n\n"
        "Output a clean, organized campaign plan with clear headings."
    ),
)

def brand_manager_node(state: MessagesState) -> Command[Literal["content_writer", END]]:
    result = brand_manager_agent.invoke(state)
    result["messages"][-1] = HumanMessage(content=result["messages"][-1].content, name="BrandManager")
    return Command(update={"messages": state["messages"] + result["messages"]}, goto=get_next_node(result["messages"][-1], "content_writer", "brand_manager"))

# LangGraph pipeline
workflow = StateGraph(MessagesState)
workflow.add_node("content_writer", content_writer_node)
workflow.add_node("graphic_designer", graphic_designer_node)
workflow.add_node("data_analyst", data_analyst_node)
workflow.add_node("brand_manager", brand_manager_node)
workflow.add_edge(START, "content_writer")
graph = workflow.compile()

def run_chatbot(user_input):
    initial_input = {"messages": [("user", user_input)]}
    conversation_transcript = []
    final_answer = None

    for event in graph.stream(initial_input, {"recursion_limit": 50}):
        for node_id, state_update in event.items():
            if isinstance(state_update, dict) and "messages" in state_update:
                for message in state_update["messages"]:
                    conversation_transcript.append(f"{message.name if hasattr(message, 'name') else node_id}: {message.content}")
                    print(f"{message.name if hasattr(message, 'name') else node_id}: {message.content}")
                    if "FINAL ANSWER" in message.content:
                        final_answer = message.content

    return conversation_transcript, final_answer

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

