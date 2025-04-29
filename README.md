# 🧠 CampaignBot: AI-Powered Campaign Assistant

> A multi-agent LLM system that generates smart, creative, and data-driven marketing campaigns using LangGraph, LangChain, and Streamlit.

![Screenshot](https://github.com/AnshulBuxy/CampaignBot/blob/main/WhatsApp%20Image%202025-04-29%20at%2018.35.30_49945f43.jpg) <!-- Replace this with your actual screenshot -->

## 🎞️Demo (Quick Preview)

Here’s a quick glimpse of theassistant in action:

![ZClap Demo](./assets/demo.gif)

> 📌 The GIF shows how it takes a product description and automatically collaborates between agents to generate a full campaign.

---

## 🚀 What Does CampaignBot Do?

It is your **AI-powered marketing team** in a box.

Provide:
- 📦 Product name  
- 📝 Description  
- 🎯 Target audience  
- 💰 Campaign budget  

It simulates a full team — Content Writer, Graphic Designer, Data Analyst, and Brand Manager — to produce a complete marketing campaign that includes:
- Catchy slogans & tone  
- Visual identity suggestions  
- Trend + market validation  
- Budget distribution  
- Influencer strategy  
- Timeline  
- KPIs & more

---

## 🧠 How It Works – LangGraph Architecture

It uses **LangGraph**, a framework built on LangChain for multi-agent workflows.  
It defines a structured graph where each agent contributes step-by-step and loops continue until the Brand Manager produces a final answer.

### 🧩 Agent Collaboration Flow

```mermaid
graph TD
    Start --> ContentWriter
    ContentWriter --> GraphicDesigner
    GraphicDesigner --> DataAnalyst
    DataAnalyst --> BrandManager
    BrandManager -->|Needs Rework| ContentWriter
    BrandManager -->|FINAL ANSWER| End

```
## 🧑‍💼 The Agents and Their Tools

### ✍️ Content Writer  
**Role:** Creative copywriting  
**Tools:**
- `RewriteTone` – rewrite text based on tone, product, and audience  
- `CopyInspo` – fetch ad slogans from Wikiquote  

---

### 🎨 Graphic Designer  
**Role:** Visual brand identity  
**Tools:**
- `PaletteGenerator` – suggest color palette by emotion  
- `FontSuggester` – suggest fonts by brand voice  

---

### 📊 Data Analyst  
**Role:** Validate ideas using real-world data  
**Tools:**
- `TrendData` – check keyword popularity with Google Trends  
- `Search` – perform external research for latest articles and trends  

---

### 🧠 Brand Manager  
**Role:** Final evaluator & decision maker  
**Tools:**
- Outputs a final structured campaign in 10 sections  

---

## ⚙️ Technologies Used

| Tool/Library       | Purpose                                   |
|--------------------|-------------------------------------------|
| **LangGraph**       | Agent coordination workflow               |
| **LangChain**       | LLM + tool interface                      |
| **Google Gemini API** | LLM for reasoning                         |
| **Streamlit**       | Interactive frontend                      |
| **pytrends**        | Scrape Google Trends data                |
| **BeautifulSoup**   | Scrape slogans from Wikiquote             |
| **pdfplumber**      | Extract text from brand books (PDFs)      |

---

## 📁 File Structure

```bash
campaign-bot/
├── campaign_tools_corrected.py        # Tools given to each agent
├── backend.py                         # LangGraph architecture & agent logic
├── app.py                             # Streamlit frontend
├── .env                               # API keys and config
└── README.md                          # You're here!
```
---

## ⚙ Installation & Setup

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
