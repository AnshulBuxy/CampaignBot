# 📣 Multi-Agent Chatbot for Campaign Design

A smart, modular chatbot that helps create effective marketing campaigns using **LangGraph**, **LangChain**, and Generative AI.

---

## 🧠 Overview

This project builds a **multi-agent chatbot** that simulates a team of experts collaborating to generate creative, data-driven marketing strategies for a product or brand. Each AI agent is responsible for a specific role in the campaign design process. The system leverages **LangGraph** to control the flow between agents and **LangChain** for handling interactions with language models. Additionally, real-world data is fetched using **TavilySearch** with **RAG (Retrieval-Augmented Generation)** techniques to enhance response accuracy.

---

## ✨ Features

- **🔗 Multi-Agent Collaboration**\
  AI agents represent key roles:

  - Content Writer
  - Graphic Designer
  - Data Analyst
  - Brand Manager

- **🧽 LangChain + LangGraph Integration**\
  LangGraph defines how agents interact, while LangChain connects to the LLM.

- **🌐 Web Search Tool**\
  The Data Analyst uses TavilySearch to pull live stats, news, and trends.

- **📚 RAG (Retrieval-Augmented Generation)**\
  Incorporates retrieved data directly into responses for better factual accuracy.

- **⚙️ Modular Design**\
  Easily extendable with more agents or features.

- **🗅️ Streamlit-Based UI**\
  Simple and clean frontend to interact with the chatbot.

---

## 🧱 Architecture

Each agent takes a turn in the conversation flow, building upon the previous agent's input:

```text
User Input ➞ Content Writer ➞ Graphic Designer ➞ Data Analyst ➞ Brand Manager ➞ Final Campaign Output
```

### 🧑‍🎼 Agents

| Agent            | Role                                                                 |
| ---------------- | -------------------------------------------------------------------- |
| Content Writer   | Creates slogans, taglines, ad copies                                 |
| Graphic Designer | Recommends themes, layouts, visual ideas                             |
| Data Analyst     | Fetches supporting data using TavilySearch                           |
| Brand Manager    | Aligns responses, ensures brand consistency, resolves contradictions |

Control flow is managed using **LangGraph**, allowing each agent to act sequentially until the **final campaign proposal** is ready.

---

## 🧠 Technologies Used

| Technology                                       | Purpose                                              |
| ------------------------------------------------ | ---------------------------------------------------- |
| **LangChain**                                    | Handles LLM-based agent responses                    |
| **LangGraph**                                    | Orchestrates the multi-agent flow                    |
| **Google Generative AI (Gemini-2.0-flash-lite)** | Main LLM for content generation                      |
| **TavilySearch**                                 | Enables real-time web search for relevant data       |
| **RAG**                                          | Blends retrieved knowledge into the responses        |
| **Streamlit**                                    | Simple UI to interact with the chatbot               |
| **Python + dotenv**                              | Backend language and environment variable management |

---

## ⚙️ Installation & Setup

### 📦 Prerequisites

- Python 3.8 or higher
- API keys for:
  - Google Generative AI
  - TavilySearch

### 🔧 Setup Steps

```bash
# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Create a .env file and add the following:
# GOOGLE_API_KEY=your_google_api_key
# TAVILY_API_KEY=your_tavily_key

# Step 3: Run the app
streamlit run app.py
```

---

## 🚀 How It Works

1. User inputs a prompt like:\
   *“Create a campaign for an eco-friendly smartwatch.”*

2. The **Content Writer** generates ad copy and slogans.

3. The **Graphic Designer** proposes visuals and branding elements.

4. The **Data Analyst** pulls data insights from the web using **TavilySearch**.

5. The **Brand Manager** reviews and finalizes the entire proposal.

6. If the campaign is not ready, the cycle continues until the system responds with:\
   **“FINAL ANSWER”**.

---

## 🖼️ Screenshots

> Replace the image paths below with your actual screenshots.

### 🧑‍🎼 Agent Interaction



### 💬 Streamlit Interface



### 🧠 Final Campaign Output



---

## 📌 Final Thoughts

This chatbot simulates a collaborative marketing team powered entirely by AI agents. It’s modular, easy to scale, and demonstrates how advanced LLM workflows like **LangGraph** can be used in real-world applications.

