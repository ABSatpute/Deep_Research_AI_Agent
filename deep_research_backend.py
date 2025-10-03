from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.chains.summarize import load_summarize_chain
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_core.tools import tool
from langchain_groq import ChatGroq
import requests
import random
import os
import re
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import streamlit as st

load_dotenv()
os.environ['LANGCHAIN_PROJECT']= 'Streamlit Deep Research'
# -------------------
# 1. LLM Initialization with Error Handling
# -------------------
def get_llm_with_fallback():
    """Get Groq LLM with proper error handling for Streamlit"""
    try:
        # Try to get API key from Streamlit secrets first, then environment
        groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
        
        if not groq_api_key:
            # If running in Streamlit, show error
            if 'streamlit' in sys.modules:
                st.error("""
                🔐 **Groq API Key Missing**
                
                Please set GROQ_API_KEY in your Streamlit secrets:
                1. Go to your app settings
                2. Click on 'Secrets'  
                3. Add: `GROQ_API_KEY = "your_key_here"`
                """)
            raise ValueError("GROQ_API_KEY not found")
            
        return ChatGroq(
            model="openai/gpt-oss-120b",
            groq_api_key=groq_api_key
        )
    except Exception as e:
        # Fallback to OpenAI if Groq fails
        openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        if openai_key:
            return ChatOpenAI(model="gpt-3.5-turbo")
        else:
            raise e

def get_llm_answer():
    """Get answer LLM with error handling"""
    try:
        groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
        if groq_api_key:
            return ChatGroq(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                groq_api_key=groq_api_key
            )
    except:
        pass
    
    # Fallback
    return get_llm_with_fallback()

# Initialize LLMs safely
try:
    llm = ChatOpenAI()  # This might also need API key handling
except:
    llm = get_llm_with_fallback()

llm_summarize = get_llm_with_fallback()
llm_answer = get_llm_answer()
title_llm = get_llm_with_fallback()

def generate_chat_title_from_messages(messages: list) -> str:
    """
    Generate a concise (3-6 word) title from the provided messages list.
    messages: list of strings (most recent conversation snippets; we'll take last 3)
    Returns a short, single-line title.
    """
    if not messages:
        return "New Chat"

    # use up to the last 3 messages to generate a short title
    relevant = "\n\n".join(messages[-3:])
    prompt = (
        "Create a very short (3-6 words) descriptive title for this recent conversation.\n"
        "Make it concise, focus on the main topic in the snippets below:\n\n"
        f"{relevant}\n\nTitle:"
    )

    try:
        # Call the LLM. Use a HumanMessage wrapper to be consistent with your existing calls
        resp = title_llm.invoke([HumanMessage(content=prompt)])
        title = getattr(resp, "content", None) or str(resp)
        # sanitize
        title = title.strip().strip('"').strip("'")
        title = re.sub(r"\s+", " ", title)
        # keep it short
        return title[:60]
    except Exception:
        # fallback to a truncated version of the most recent snippet
        return relevant[:50].strip() + "..."

# Rest of your code remains the same...
# -------------------
# 2. Tools
# -------------------
# Tools
@tool
def deep_research(query: str) -> dict:
    """
    Perform deep research on a query using Tavily search.
    Returns structured summaries in key-value format.
    """
    tavily = TavilySearchResults()
    docs = tavily.run(query)
    results = []

    for d in docs:
        content = d.get("content") if isinstance(d, dict) else str(d)
        title = d.get("title", "No Title Found") if isinstance(d, dict) else "No Title Found"
        url = d.get("url", "") if isinstance(d, dict) else ""

        # Clean text
        cleaned = re.sub(r"http\S+|[^\w\s]", "", content).strip()

        # Summarize
        if len(cleaned) < 1000:
            summary = llm_summarize.invoke(cleaned).content
        else:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = [Document(page_content=t) for t in text_splitter.split_text(cleaned)]
            summarize_chain = load_summarize_chain(llm_summarize, chain_type="map_reduce")
            summary = summarize_chain.run(chunks)

        results.append({
            "title": title,
            "url": url,
            "summary": summary
        })

    return {"results": results}


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=OXNRQGMJ9ZTHCD6F"
    r = requests.get(url)
    return r.json()

@tool
def get_weather_data(city: str) -> str:
    """
    Fetch current weather information for a given location.
    """
    url = f'https://api.weatherstack.com/current?access_key=42313f0f342da949f4773a35db13124f={city}'
    response = requests.get(url)
    return response.json()

tools = [deep_research, get_stock_price, calculator, get_weather_data]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------   
def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages":[response]}

tool_node = ToolNode(tools)

# -------------------
# 5. Checkpointer
# -------------------
conn = sqlite3.connect(database= "research_agent.db", check_same_thread= False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 6. Graph
# -------------------
# graph structure
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
# If the llm asked for a tool, go to Tool Node; else finish
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")
research_agent = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
def retrieve_all_threads():
    all_thread = set()
    for cheackpoint in checkpointer.list(None):
        all_thread.add(cheackpoint.config['configurable']['thread_id'])
        
    return list(all_thread)


