
import random
import requests
import json
from bs4 import BeautifulSoup
from langchain.tools import Tool
import pdfplumber
from pytrends.request import TrendReq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0,
    timeout=None,
    max_retries=2,
)

# Content Writer Tools


def rewrite_tone_tool(input_str):
    try:
        inputs = json.loads(input_str)
        text = inputs.get("text", "")
        product_description = inputs.get("product_description", "")
        target_audience = inputs.get("target_audience", "")

        prompt = f"""
You are a tone analyst and copywriter.

1. Decide the appropriate tone (bold, minimalist, emotional, fun, luxurious, etc.) based on the product and target audience.
2. Rewrite the given copy in the decided tone.

Product: {product_description}
Target Audience: {target_audience}

Original Copy:
{text}

Return only the rewritten copy.
"""
        return llm.invoke(prompt).content
    except Exception as e:
        return f"Error: {str(e)}"

def copy_inspo_tool(input_str):
    try:
        query = input_str.strip()
        url = f"https://en.wikiquote.org/w/index.php?search={query}+advertising"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        quotes = [q.text.strip() for q in soup.select("ul li") if len(q.text) < 180]
        return random.sample(quotes, min(3, len(quotes))) if quotes else ["No good quotes found."]
    except Exception as e:
        return ["Error fetching quotes."]

content_writer_tools = [
    Tool(
        name="RewriteTone",
        func=rewrite_tone_tool,
        description="Rewrite text for the campaign. Input must be a JSON string: {\"text\": ..., \"product_description\": ..., \"target_audience\": ...}"
    ),
    Tool(
        name="CopyInspo",
        func=copy_inspo_tool,
        description="Fetch catchy advertising quotes. Input must be the product/topic string."
    )
]


# Graphic Designer Tools


def palette_generator_tool(input_str):
    emotion = input_str.lower().strip()
    palettes = {
        "calm": ["#A8DADC", "#457B9D", "#1D3557"],
        "energetic": ["#FF6B6B", "#FFE66D", "#4472CA"],
        "luxury": ["#0D0D0D", "#FFD700", "#8B4513"],
        "eco": ["#2E8B57", "#6B8E23", "#8FBC8F"],
        "trust": ["#0077B6", "#90E0EF", "#CAF0F8"],
        "youthful": ["#FFB5E8", "#FF9CEE", "#B28DFF"],
        "techy": ["#0F4C75", "#3282B8", "#BBE1FA"],
        "bold": ["#D7263D", "#3F88C5", "#F49D37"],
        "friendly": ["#FFB347", "#FF6961", "#77DD77"],
        "elegant": ["#2C2C2C", "#B0A990", "#EDE6DB"]
    }
    return palettes.get(emotion, ["#FFFFFF", "#000000"])

def font_suggester_tool(input_str):
    brand_voice = input_str.lower().strip()
    suggestions = {
        "modern": ["Helvetica", "Futura", "Proxima Nova", "Avenir"],
        "playful": ["Comic Sans MS", "Poppins", "Baloo", "Quicksand"],
        "luxury": ["Didot", "Bodoni", "Garamond", "Playfair Display"],
        "minimalist": ["Roboto", "Open Sans", "Montserrat", "Source Sans Pro"],
        "tech": ["Orbitron", "Titillium Web", "Exo 2"],
        "handwritten": ["Pacifico", "Dancing Script", "Amatic SC"],
        "vintage": ["Rockwell", "Baskerville", "Courier"],
        "bold": ["Impact", "Anton", "Bebas Neue"],
        "elegant": ["Cormorant Garamond", "Libre Baskerville", "Georgia"]
    }
    return suggestions.get(brand_voice, ["Arial", "Times New Roman"])

graphic_designer_tools = [
    Tool(
        name="PaletteGenerator",
        func=palette_generator_tool,
        description="Suggest a color palette based on an emotion. Input is the emotion as a simple string."
    ),
    Tool(
        name="FontSuggester",
        func=font_suggester_tool,
        description="Suggest fonts based on brand voice. Input is the brand voice string."
    )
]


# Data Analyst Tools


def trend_data_tool(input_str):
    keyword = input_str.strip()
    pytrends = TrendReq()
    pytrends.build_payload([keyword], timeframe='today 3-m')
    data = pytrends.interest_over_time()
    if not data.empty:
        return data[keyword].to_dict()
    else:
        return {"message": "No trend data found."}
search = TavilySearchResults(max_results=2)

data_analyst_tools = [
    Tool(
        name="TrendData",
        func=trend_data_tool,
        description="Fetch recent Google Trends data for a given keyword. Input is the keyword as a simple string."
    ),
    Tool(name="DataSearch", func=search.run, description="Use this tool to get relevant data and insights.")
]

# Brand Manager Tools


def brand_book_reader_tool(input_str):
    file_path = input_str.strip()
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages[:5]:
                text += page.extract_text() + "\n"
        prompt = f"Summarize the following brand guideline:\n\n{text}"
        return llm.invoke(prompt).content
    except Exception as e:
        return "Error reading brand book."

brand_manager_tools = [
    Tool(
        name="BrandBookReader",
        func=brand_book_reader_tool,
        description="Upload a brand book PDF and get a summarized overview. Input must be the file path string."
    )
]
