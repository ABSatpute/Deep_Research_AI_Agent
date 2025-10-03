<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
</head>
<body>
  <h1>Deep Research AI Agent</h1>

  <p>
    An AI-powered research assistant that leverages advanced language models, LangGraph, and live web search to deliver structured, high-quality answers to complex user queries. The agent automates information retrieval, summarization, synthesis, and provides an interactive UI with Streamlit.
  </p>

  <h2>✨ Features</h2>
  <ul>
    <li><strong>Multi-step AI Workflow</strong> - Automates research using LangGraph state graphs.</li>
    <li><strong>Live Web Search</strong> - Integrates Tavily API for real-time content.</li>
    <li><strong>Smart Text Processing</strong> - Cleans and summarizes using LLMs (Groq LLaMA, OpenAI GPT).</li>
    <li><strong>Structured Outputs</strong> - Research is returned with titles, URLs, and summaries.</li>
    <li><strong>Streamlit Frontend</strong> - Interactive chat UI with thread management and titles.</li>
    <li><strong>Secure API Integration</strong> - Keys managed via Streamlit secrets or environment.</li>
    <li><strong>SQLite Checkpointing</strong> - Persistent conversation state with thread retrieval.</li>
  </ul>

  <h2>🔧 Getting Started</h2>
  <h3>1. Clone the Repository</h3>
  <pre><code>git clone https://github.com/ABSatpute/deep-research-ai-agent.git
cd deep-research-ai-agent</code></pre>

  <h3>2. Install Dependencies</h3>
  <pre><code>pip install -r requirements.txt</code></pre>

  <h3>3. Set Up API Keys</h3>
  <p>
    - Get a <strong>Tavily API Key</strong> from <a href="https://tavily.com" target="_blank">Tavily</a><br/>
    - Get a <strong>Groq API Key</strong> from <a href="https://console.groq.com" target="_blank">Groq</a><br/>
    - Optionally, set an <strong>OpenAI API Key</strong> if fallback is needed.
  </p>

  <pre><code>
import os

os.environ["TAVILY_API_KEY"] = "your_tavily_key"
os.environ["GROQ_API_KEY"] = "your_groq_key"
os.environ["OPENAI_API_KEY"] = "your_openai_key"  # optional
</code></pre>

  <h2>📈 How It Works</h2>
  <ol>
    <li>User submits a natural-language research query via Streamlit UI.</li>
    <li>Relevant web content is fetched via Tavily API.</li>
    <li>Results are cleaned and summarized using Groq/OpenAI LLMs.</li>
    <li>The info is structured with title, URL, and summary.</li>
    <li>A final concise synthesis is generated and displayed.</li>
  </ol>

  <h2>🧪 Example Usage</h2>
  <pre><code>
# Running locally
streamlit run deep_research_frontend.py

# Example query inside the app:
"What are the latest advancements in quantum computing?"
</code></pre>

  <h2>📁 Project Structure</h2>
  <ul>
    <li><code>deep_research_backend.py</code> - Backend logic, LangGraph agent</li>
    <li><code>deep_research_frontend.py</code> - Streamlit UI for interaction</li>
    <li><code>research_agent.db</code> - SQLite checkpoint database</li>
    <li><code>README.html</code> - This file</li>
    <li><code>requirements.txt</code> - Dependency list</li>
  </ul>

  <h2>💡 Use Cases</h2>
  <ul>
    <li>Academic research automation</li>
    <li>Writing support and background research</li>
    <li>Market and competitive analysis</li>
    <li>Technology scouting and summaries</li>
    <li>Personal research assistant with persistent threads</li>
    <li>Real-time news and trending topics research</li>
    <li>Stock prices and financial insights</li>
    <li>Weather updates and forecasts</li>
  </ul>

  <h2>🚀 Live Demo</h2>
<p>
  Try the deployed app here:  
  <a href="https://akash-deep-research-ai-agent.streamlit.app/" target="_blank">
    🌐 Deep Research AI Agent (Streamlit App)
  </a>
</p>

  <h2>📜 License</h2>
  <p>Distributed under the <a href="LICENSE">MIT License</a>.</p>

  <h2>📬 Contact</h2>
  <p>
    Author: Akash Satpute<br/>
    GitHub: <a href="https://github.com/ABSatpute" target="_blank">ABSatpute</a><br/>
    Email: <a href="mailto:ab31satpute@gmail.com">ab31satpute@gmail.com</a>
  </p>

  <p><em>Made with ❤️ to simplify deep research tasks!</em></p>

</body>
</html>
