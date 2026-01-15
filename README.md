# LangChain & Gemini Agent Tools - Learning Project

A comprehensive learning project exploring agentic AI implementations using Google's Gemini 2.5 Flash, progressing from basic tool-calling to sophisticated multi-agent orchestration.

## 🎯 Project Overview

This repository demonstrates three progressive approaches to building AI agents with tool-calling capabilities:

1. **Basic Agent** - Direct Gemini SDK implementation (no LangChain)
2. **LangChain Agent** - Single agent with LangChain abstractions
3. **Multi-Agent System** - Hierarchical agents with automatic routing

## 📁 Project Structure

```
lg-tools/
├── basic-agent.py          # Native Gemini SDK implementation
├── lg-agent.py             # Simple LangChain agent
├── lg-multi-agent.py       # Multi-agent orchestration system
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
└── utils/
    ├── tools.py           # Tool definitions (math, weather, research, text)
    └── helpers.py         # Utility functions for message parsing
```

## 🚀 Features

- ✅ **Gemini 2.5 Flash Integration** - Latest Google AI model
- ✅ **Function Calling / Tool Use** - LLM decides when to use tools
- ✅ **FastAPI REST Endpoints** - Production-ready HTTP APIs
- ✅ **Multi-Agent Architecture** - Specialized agents with automatic routing
- ✅ **Environment Configuration** - Secure API key management
- ✅ **Comprehensive Tool Library** - 8+ pre-built tools

## 🛠️ Available Tools

### Math Tools
- `calculator` - Basic operations (add, subtract, multiply, divide)
- `advanced_calculator` - Complex expression evaluation
- `analyze_data` - Statistical analysis (count, sum, avg, min, max)
- `filter_data` - Filter datasets by threshold

### Weather Tools
- `get_weather` - Current weather for cities (mock data)
- `get_forecast` - Multi-day weather forecast (1-7 days)

### Research Tools
- `search_database` - Query mock database (users/products)
- `text_analyzer` - Text statistics (word count, character count, etc.)

## 📦 Installation

### 1. Clone & Navigate
```bash
cd /path/to/lg-tools
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## 🎮 Usage

### Option 1: Basic Agent (Native Gemini SDK)

**Features:**
- Direct Gemini SDK usage (no LangChain)
- Manual function calling implementation
- Optimized comprehensions for parsing

**Run:**
```bash
python basic-agent.py
# Server runs at http://0.0.0.0:8000
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 25 + 37?"}'
```

**Response:**
```json
{
  "answer": "The result is 62.",
  "tool_used": "calculator",
  "tool_result": {"result": 62}
}
```

---

### Option 2: LangChain Agent (Single Agent)

**Features:**
- LangChain 0.3+ agent implementation
- Simplified agent creation
- 2 tools: calculator, get_weather

**Run:**
```bash
python lg-agent.py
# Server runs at http://0.0.0.0:8001
```

**Example Request:**
```bash
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Paris?"}'
```

**Response:**
```json
{
  "answer": "The current weather in Paris is sunny with a temperature of 18°C and humidity at 60%.",
  "intermediate_steps": null
}
```

---

### Option 3: Multi-Agent System (Automatic Routing)

**Features:**
- **Hierarchical agent architecture** with 4 specialized agents:
  - **Math Agent** - Handles calculations and data analysis
  - **Weather Agent** - Provides weather information
  - **Research Agent** - Database searches and text analysis
  - **General Agent** - Routes queries to specialized agents
- **Automatic LLM-based routing** - General agent uses sub-agents as tools
- Each specialized agent has focused tools and expertise

**Run:**
```bash
python lg-multi-agent.py
# Server runs at http://0.0.0.0:8001
```

**Example Requests:**

**Math Query:**
```bash
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "Calculate the average of [10, 20, 30, 40, 50]"}'
```

**Weather Query:**
```bash
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the 5-day forecast for Tokyo?"}'
```

**Research Query:**
```bash
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "Search for all users in the database"}'
```

**Response Format:**
```json
{
  "answer": "The 5-day forecast for Tokyo is: Clear, Clear, Cloudy, Rainy, Clear.",
  "intermediate_steps": null
}
```

---

## 🏗️ Architecture

### Basic Agent Flow
```
User Query → Gemini Model → Function Call Decision → Tool Execution → Final Response
```

### LangChain Agent Flow
```
User Query → LangChain Agent → Tool Selection → Tool Execution → Response Formatting
```

### Multi-Agent System Flow
```
User Query 
    ↓
General Agent (Router)
    ↓
Analyzes Intent & Selects Specialized Agent
    ↓
┌──────────────┬──────────────┬──────────────┐
│  Math Agent  │Weather Agent │Research Agent│
└──────────────┴──────────────┴──────────────┘
    ↓
Specialized Agent Executes Tools
    ↓
Final Response
```

**How Multi-Agent Routing Works:**
1. General agent receives query
2. LLM analyzes query intent and content
3. General agent calls appropriate specialized agent as a tool
4. Specialized agent executes its domain-specific tools
5. Result is returned through the hierarchy

## 🔧 API Endpoints

### All Agents
- `POST /agent` - Process query with agent
- `GET /health` - Health check

### Request Schema
```json
{
  "query": "string"  // User's question or command
}
```

### Response Schema (varies by implementation)

**Basic Agent:**
```json
{
  "answer": "string",
  "tool_used": "string | null",
  "tool_result": "object | null"
}
```

**LangChain & Multi-Agent:**
```json
{
  "answer": "string",
  "intermediate_steps": "array | null"
}
```

## 🧪 Testing Examples

### Python Requests
```python
import requests

response = requests.post(
    "http://localhost:8001/agent",
    json={"query": "What's 15 multiplied by 8?"}
)
print(response.json())
```

### cURL
```bash
# Math
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "Evaluate: 2**8 + 100"}'

# Weather
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "Current weather in London?"}'

# Text Analysis
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze this text: Hello world from AI agents"}'
```

## 📚 Key Concepts Learned

### 1. Tool Calling / Function Calling
- LLMs decide when and which tools to use
- Tools extend LLM capabilities beyond text generation
- Structured input/output schemas for reliable execution

### 2. Agent Patterns
- **ReAct Loop**: Reasoning → Action → Observation → Repeat
- **Single Agent**: One model with multiple tools
- **Multi-Agent**: Specialized agents orchestrated by a coordinator

### 3. LangChain Abstractions
- `create_agent()` - Simplified agent creation
- `@tool` decorator - Easy tool definition
- Message-based state management
- Structured output with Pydantic models

### 4. Production Considerations
- Environment-based configuration
- Error handling and validation
- FastAPI for production-ready APIs
- Modular code organization (utils/)

## 🐛 Troubleshooting

### Issue: "GOOGLE_API_KEY is not set"
**Solution:** Create `.env` file with your API key:
```bash
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Issue: Import errors
**Solution:** Install all dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Pydantic validation errors with message content
**Solution:** Already handled! The `extract_text_from_message()` helper in `utils/helpers.py` handles both string and multi-part content structures from Gemini responses.

### Issue: Port already in use
**Solution:** Change port in the `uvicorn.run()` call or kill existing process:
```bash
lsof -ti:8000 | xargs kill -9  # Kill process on port 8000
```

## 📖 Learning Path

1. **Start with `basic-agent.py`**
   - Understand raw Gemini SDK
   - See function calling mechanics
   - Learn request/response parsing

2. **Move to `lg-agent.py`**
   - LangChain abstractions
   - Simplified agent creation
   - Message-based workflows

3. **Explore `lg-multi-agent.py`**
   - Multi-agent architecture
   - Automatic routing logic
   - Agent composition patterns

## 🔗 Resources

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [LangChain Agents Guide](https://docs.langchain.com/oss/python/langchain/agents)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Models](https://docs.pydantic.dev/)

## 📝 License

This is a learning project for educational purposes.

## 🤝 Contributing

Feel free to experiment, break things, and learn! This is a sandbox for exploring agentic AI patterns.

---

**Happy Learning! 🚀**
