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

load_dotenv()
os.environ['LANGCHAIN_PROJECT'] = 'deep research agent'

# -------------------
# 1. LLM
# -------------------
llm = ChatOpenAI()
llm_summarize = ChatGroq(model="openai/gpt-oss-120b")
llm_answer = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")
title_llm = ChatGroq(model="openai/gpt-oss-120b")

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
            from langchain_groq import ChatGroq
            llm_summarize = ChatGroq(model="openai/gpt-oss-120b")
            summary = llm_summarize.invoke(cleaned).content
        else:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = [Document(page_content=t) for t in text_splitter.split_text(cleaned)]
            from langchain_groq import ChatGroq
            llm_summarize = ChatGroq(model="openai/gpt-oss-120b")
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

    This tool queries a weather data source (e.g., an API or local service)
    to return the latest weather conditions such as temperature, humidity,
    and description. It is intended to provide real-time information that
    the LLM alone cannot generate reliably.

    Parameters
    ----------
    location : str
        The name of the city, region, or location for which to fetch
        the weather information.


    Notes
    -----
    - This tool should be invoked by the workflow when weather data
      is specifically requested.
    - The function does not modify or return the entire workflow state,
      only updates with relevant weather information.
    - Error handling (e.g., invalid location, API errors) should be added
      in production.
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
# out = deep_research.invoke({"messages":[HumanMessage(content="hello!")]})
# print(out['messages'][-1].content)

# while True:
#     user_message= input("Type Here :")
#     print("User :", user_message)
    
#     if user_message.strip().lower() in ["exit", "q", "quit", "bye"]:
#         break
    
#     response = deep_research.invoke({'messages': HumanMessage(content=user_message)})

#     print("AI:", response["messages"][-1].content)
