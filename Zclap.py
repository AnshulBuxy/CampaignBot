import getpass
import os
from typing import Literal,List

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.graph import MessagesState
from langchain.tools import Tool
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0,
    timeout=None,
    max_retries=2,
    # other params...
)
# Initialize the LLM (using Anthropic's Claude 3.5 Sonnet in this example)
#llm =ChatMistralAI(model_name="mistral-large-latest")

def make_system_prompt(role_desc: str) -> str:
    return (
        "You are a helpful AI assistant collaborating with other assistants. "
        "Use your expertise to advance the campaign design. "
        "If you or any colleague have the final campaign proposal, prefix your response with FINAL ANSWER so the team stops."
        f"\nRole instructions: {role_desc}"
    )

# Utility: Determine next node based on the last message content.
def get_next_node(last_message: BaseMessage, goto: str):
    if "FINAL ANSWER" in last_message.content:
        return END
    return goto

# 1. Content Writer Agent
content_writer_agent = create_react_agent(
    llm,
    tools=[],  # No external tools needed in this example
    prompt=make_system_prompt(
        "You are the Content Writer. Generate creative campaign slogans, taglines, and copy for a new product launch."
    ),
)

def content_writer_node(state: MessagesState) -> Command[Literal["graphic_designer", END]]:
    result = content_writer_agent.invoke(state)
    # Wrap the output as a human message with agent name tag
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="ContentWriter"
    )
    next_node = get_next_node(result["messages"][-1], "graphic_designer")
    return Command(update={"messages": result["messages"]}, goto=next_node)

# 2. Graphic Designer Agent
graphic_designer_agent = create_react_agent(
    llm,
    tools=[],
    prompt=make_system_prompt(
        "You are the Graphic Designer. Propose visual themes, color schemes, and layout ideas for the campaign. "
        "If you disagree with a proposal (e.g., you prefer a minimalist look), state your reasoning."
    ),
)

def graphic_designer_node(state: MessagesState) -> Command[Literal["data_analyst", END]]:
    result = graphic_designer_agent.invoke(state)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="GraphicDesigner"
    )
    next_node = get_next_node(result["messages"][-1], "data_analyst")
    return Command(update={"messages": result["messages"]}, goto=next_node)

# 3. Data Analyst Agent
search = TavilySearchResults(max_results=2)
DataSearch_tool= Tool(name="DataSearch", func=search.run, description="Use this tool to get relevant data and insights.")
data_analyst_agent = create_react_agent(
    llm,
    tools=[DataSearch_tool],
    prompt=make_system_prompt(
        "You are the Data Analyst. Provide market insights, target demographics, and performance metrics that can support campaign ideas. "
        "Offer data to validate or challenge creative proposals. you can use the DataSearch_tool to find relevant data."
    ),
)

def data_analyst_node(state: MessagesState) -> Command[Literal["brand_manager", END]]:
    result = data_analyst_agent.invoke(state)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="DataAnalyst"
    )
    next_node = get_next_node(result["messages"][-1], "brand_manager")
    return Command(update={"messages": result["messages"]}, goto=next_node)

# 4. Brand Manager Agent
brand_manager_agent = create_react_agent(
    llm,
    tools=[],
    prompt=make_system_prompt(
        "You are the Brand Manager. Evaluate all inputs to ensure they align with the brand identity. "
        "If conflicts arise (e.g., neon versus minimalist aesthetics), resolve them and finalize the campaign message."
    ),
)

def brand_manager_node(state: MessagesState) -> Command[Literal["content_writer", END]]:
    result = brand_manager_agent.invoke(state)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="BrandManager"
    )
    # After Brand Manager, cycle back to Content Writer unless a FINAL ANSWER is reached.
    next_node = get_next_node(result["messages"][-1], "content_writer")
    return Command(update={"messages": result["messages"]}, goto=next_node)

# Build the state graph and add the agent nodes
workflow = StateGraph(MessagesState)
workflow.add_node("content_writer", content_writer_node)
workflow.add_node("graphic_designer", graphic_designer_node)
workflow.add_node("data_analyst", data_analyst_node)
workflow.add_node("brand_manager", brand_manager_node)

# Start with the Content Writer agent
workflow.add_edge(START, "content_writer")

# Compile the graph
graph = workflow.compile()

import streamlit as st
from langgraph.graph import MessagesState

# Function to interact with the chatbot
def run_chatbot(user_input):
    initial_input = {"messages": [("user", user_input)]}
    conversation_transcript = []
    final_answer = None
    
    for event in graph.stream(initial_input, {"recursion_limit": 50}):
        for node_id, state_update in event.items():
            if isinstance(state_update, dict) and "messages" in state_update:
                for message in state_update["messages"]:
                    conversation_transcript.append(f"{message.name if hasattr(message, 'name') else node_id}: {message.content}")
                    if "FINAL ANSWER" in message.content:
                        final_answer = message.content
    
    return conversation_transcript, final_answer

# Streamlit UI
st.title("🧠 AI-Powered Campaign Assistant")
st.write("Chat with our AI agents to generate marketing campaigns.")

# User Input
user_input = st.text_area("Enter your campaign request:", "Create a campaign for an eco-friendly smartwatch.")

if st.button("Generate Campaign"):
    with st.spinner("Generating campaign..."):
        transcript, final_answer = run_chatbot(user_input)
        
        # st.subheader("Agent Conversation Transcript:")
        # for line in transcript:
        #     st.write(line)
        
        if final_answer:
            st.subheader("Final Campaign Proposal:")
            st.write(final_answer)
        else:
            st.warning("No final answer was generated within the conversation.")