 <h1>Deep Research AI Agent</h1>

  <p>
    An AI-powered research assistant that leverages advanced language models and live web search to deliver structured, high-quality answers to complex user queries. The agent automates information retrieval, summarization, and synthesis, making it ideal for research-heavy tasks.
  </p>

  <h2>✨ Features</h2>
  <ul>
    <li><strong>Multi-step AI Workflow</strong> - Automates research using LangGraph.</li>
    <li><strong>Live Web Search</strong> - Integrates Tavily API for real-time content.</li>
    <li><strong>Smart Text Processing</strong> - Cleans and summarizes using LLMs (Mixtral, DeepSeek).</li>
    <li><strong>Structured Outputs</strong> - Research is returned with titles, URLs, and summaries.</li>
    <li><strong>Interactive CLI Support</strong></li>
    <li><strong>Secure API Integration</strong></li>
  </ul>


  <h2>🔧 Getting Started</h2>
  <h3>1. Clone the Repository</h3>
  <pre><code>git clone https://github.com/your-username/deep-research-ai-agent.git
cd deep-research-ai-agent</code></pre>

  <h3>2. Install Dependencies</h3>
  <pre><code>pip install langgraph langsmith langchain_groq langchain_community tavily-python</code></pre>

  <h3>3. Set Up API Keys</h3>
  <p>
    - Get a <strong>Tavily API Key</strong> from <a href="https://tavily.com" target="_blank">Tavily</a><br/>
    - Get a <strong>Groq API Key</strong> from <a href="https://console.groq.com" target="_blank">Groq</a><br/>
  </p>

  <pre><code>
from google.colab import userdata
import os

groq_api_key = userdata.get("groq_api_key")
tavily_api_key = userdata.get("tavily_api_key")

os.environ["TAVILY_API_KEY"] = tavily_api_key
os.environ["GROQ_API_KEY"] = groq_api_key
  </code></pre>

  <h2>📈 How It Works</h2>
  <ol>
    <li>User submits a natural-language research query.</li>
    <li>Relevant web content is fetched via Tavily API.</li>
    <li>Results are cleaned and summarized using Mixtral LLM.</li>
    <li>The info is structured with title, URL, and summary.</li>
    <li>DeepSeek LLM generates a final concise synthesis.</li>
  </ol>

  <h2>🧪 Example Usage</h2>
  <pre><code>
results, final_answer = run_agent("What are the latest advancements in quantum computing?")
print("Summary of Sources:\n")
for res in results:
    print(res['title'], res['url'])
    print(res['summary'])

print("\nSynthesized Answer:\n", final_answer)
  </code></pre>

  <h2>📁 Project Structure</h2>
  <ul>
    <li><code>Deep_Research_AI_Agent_final-1.ipynb</code> - Main notebook</li>
    <li><code>README.html</code> - This file</li>
    <li><code>requirements.txt</code> - Dependency list</li>
  </ul>

  <h2>💡 Use Cases</h2>
  <ul>
    <li>Academic research automation</li>
    <li>Writing support and background research</li>
    <li>Market and competitive analysis</li>
    <li>Technology scouting and summaries</li>
  </ul>

  <h2>📜 License</h2>
  <p>Distributed under the <a href="LICENSE">MIT License</a>.</p>

  <h2>📬 Contact</h2>
  <p>
    Author: Akash Satpute<br/>
    GitHub: <a href="(https://github.com/ABSatpute/)" target="_blank">ABSatpute</a><br/>
    Email: <a href="ab31satpute@gmail.com">ab31satpute@gmail.com</a>
  </p>

  <p><em>Made with ❤️ to simplify deep research tasks!</em></p>

</body>
</html>
