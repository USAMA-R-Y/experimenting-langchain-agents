# LangChain & Gemini Agent Tools - Learning Project

A comprehensive learning project exploring agentic AI implementations using Google's Gemini 2.5 Flash, progressing from basic tool-calling to sophisticated multi-agent orchestration.

## 🎯 Project Overview

This repository demonstrates four progressive approaches to building AI agents with tool-calling capabilities:

1. **Basic Agent** - Direct Gemini SDK implementation (no LangChain)
2. **LangChain Agent** - Single agent with LangChain abstractions
3. **Multi-Agent Sync** - Sequential pipeline where each tool depends on previous outputs
4. **Multi-Agent Async** - Parallel execution for high-throughput support ticket processing

## 📁 Project Structure

```
lg-tools/
├── 1_basic_agent.py              # Native Gemini SDK implementation
├── 2_lg-agent.py                 # Simple LangChain agent
├── 3_lg_multi_agent_sync.py      # Sequential pipeline with dependencies
├── 4_lg_multi_agent_async.py     # Parallel async execution
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (create this)
└── utils/
    ├── tools.py                 # Tool definitions (50+ tools)
    └── helpers.py               # Utility functions for message parsing
```

## 🚀 Features

- ✅ **Gemini 2.5 Flash Integration** - Latest Google AI model
- ✅ **Function Calling / Tool Use** - LLM decides when to use tools
- ✅ **FastAPI REST Endpoints** - Production-ready HTTP APIs
- ✅ **Sequential Pipeline** - Tools depend on previous tool outputs (Sync)
- ✅ **Parallel Execution** - Concurrent agent processing (Async)
- ✅ **Environment Configuration** - Secure API key management
- ✅ **Comprehensive Tool Library** - 50+ pre-built tools for support tickets

## 🛠️ Available Tools

### Math Tools
- `calculator` - Basic operations (add, subtract, multiply, divide)
- `advanced_calculator` - Complex expression evaluation
- `analyze_data` - Statistical analysis (count, sum, avg, min, max)
- `filter_data` - Filter datasets by threshold

### Weather Tools
- `get_weather` - Current weather via WeatherAPI (needs WEATHER_API_KEY)
- `get_forecast` - Multi-day forecast (1-7 days) via WeatherAPI

### Research Tools
- `search_database` - Query mock database (users/products)
- `text_analyzer` - Text statistics (word count, character count, etc.)

### Support Ticket Tools (Used in Sync/Async Multi-Agent Systems)

**Sentiment Analysis:**
- `analyze_sentiment` - Analyzes overall sentiment (positive/negative/neutral)
- `detect_urgency` - Detects urgency level and priority
- `classify_emotion` - Classifies primary emotions (anger, joy, frustration, etc.)

**Knowledge Base:**
- `search_docs` - Searches documentation and help articles
- `find_similar_tickets` - Finds similar past support tickets
- `get_solution_steps` - Gets step-by-step solutions for common issues

**Customer Context:**
- `get_customer_profile` - Retrieves customer profile information
- `fetch_purchase_history` - Fetches customer's purchase history
- `check_subscription_status` - Checks subscription status and renewal

**System Status:**
- `check_service_status` - Checks current status of all services
- `get_known_issues` - Retrieves list of known issues
- `check_outages` - Checks for any current service outages

**Response Generation:**
- `generate_response` - Generates appropriate response based on context
- `apply_tone_guidelines` - Applies appropriate tone based on sentiment
- `suggest_next_steps` - Suggests next steps for customer or support team

## 📒 Tool Guidelines (Purpose, Use-case, How to Use)

### Math
- **calculator**
  - Purpose: Quick arithmetic (add/subtract/multiply/divide).
  - Use-case: Fast numeric answers, totals, or simple sanity checks.
  - How: Provide `operation` and numbers, e.g., prompt: “add 42 and 58”.
- **advanced_calculator**
  - Purpose: Evaluate expressions (e.g., `2**3 + 5*4`).
  - Use-case: Formula-style inputs or chained math.
  - How: Prompt with the expression string.
- **analyze_data**
  - Purpose: Basic stats over a list of numbers.
  - Use-case: Quick summary (count, sum, avg, min, max).
  - How: Supply `data` as a list of floats.
- **filter_data**
  - Purpose: Filter numbers by threshold and comparison.
  - Use-case: Keep numbers greater/less/equal to a threshold.
  - How: Provide `data`, `threshold`, `operation` in {greater, less, equal}.

### Weather (WeatherAPI-backed)
- **get_weather**
  - Purpose: Current conditions for a city.
  - Use-case: “What’s the weather in Lahore right now?”
  - How: Provide `city`; needs `WEATHER_API_KEY` in `.env`. Returns city/region/country, lat/lon, tz, localtime, temps (C/F), condition, humidity, wind, pressure, precip, feelslike, UV, plus `raw`.
- **get_forecast**
  - Purpose: 1–7 day forecast summary.
  - Use-case: “Give me a 3-day forecast for London.”
  - How: Provide `city`, `days` (1–7); needs `WEATHER_API_KEY`. Returns location info and `forecast_days` with temps, wind, precip, humidity, rain/snow chances, condition, plus `raw`.

### Research / Text
- **search_database**
  - Purpose: Mock search over users/products.
  - Use-case: “Find all users” or “List products.”
  - How: Provide `query` string; returns matching mock records.
- **text_analyzer**
  - Purpose: Text stats.
  - Use-case: “Analyze this paragraph” for counts/lengths.
  - How: Provide `text`; returns character/word/sentence counts and avg word length.

### Response Handling Helpers (internal)
- `extract_text_from_message`, `safe_extract_from_result`, `extract_function_call_from_response`, `extract_text_from_response` live in `utils/helpers.py` to normalize model outputs and function calls.

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
python 1_basic_agent.py
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
python 2_lg-agent.py
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

### Option 3: Multi-Agent Synchronous (Sequential Pipeline with Dependencies)

**Features:**
- **6-Step Sequential Pipeline** - Each tool depends on previous tool outputs
- **Data Flow Architecture** - Information accumulates and flows forward through the pipeline
- **Support Ticket Processing** - Realistic customer support use case
- **Orchestrator Agent** - Coordinates execution and ensures proper sequencing

**Pipeline Architecture:**
```
STEP 1: Sentiment Analysis (analyzes message)
   ↓ output feeds into...
STEP 2: Urgency Detection (uses sentiment + message)
   ↓ output feeds into...
STEP 3: Knowledge Search (uses urgency + message)
   ↓ output feeds into...
STEP 4: Customer Context (uses knowledge + customer_id)
   ↓ output feeds into...
STEP 5: System Status (uses customer context)
   ↓ output feeds into...
STEP 6: Response Generation (uses ALL previous outputs)
```

**Run:**
```bash
python 3_lg_multi_agent_sync.py
# Server runs at http://0.0.0.0:8001
```

**Endpoints:**
- `POST /support/process` - Process a support ticket through sequential pipeline
- `GET /health` - Health check with agent list
- `GET /` - System information and pipeline documentation

**Request Schema:**
```json
{
  "id": "T-12345",
  "customer_id": "C001",
  "message": "I am very frustrated! My login is not working and I need access urgently!"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8001/support/process \
  -H "Content-Type: application/json" \
  -d '{
    "id": "T-12345",
    "customer_id": "C001",
    "message": "I cannot login and need urgent help!"
  }'
```

**Response Format:**
```json
{
  "ticket_id": "T-12345",
  "response": "Comprehensive personalized support response based on all 6 steps...",
  "metadata": {
    "customer_id": "C001",
    "processing_type": "synchronous_pipeline",
    "steps": 6,
    "message_count": 15
  }
}
```

**Use Cases:**
- Learning tool dependencies and data flow
- Sequential reasoning requirements
- When each step truly depends on previous analysis
- Understanding agent orchestration patterns

---

### Option 4: Multi-Agent Async (Parallel Execution)

**Features:**
- **5 Specialized Agents** running in **parallel** (no dependencies)
- **Async/Await Pattern** - Uses `asyncio.gather()` for concurrent execution
- **Error Resilience** - Individual agent failures don't break the pipeline
- **High Throughput** - Reduces latency from ~15s (sequential) to ~3-4s (parallel)

**Architecture:**
```
                    User Ticket
                        ↓
        ┌───────────────┴───────────────┐
        ↓               ↓               ↓
   [Sentiment]    [Knowledge]    [Customer]    [Status]
        ↓               ↓               ↓          ↓
        └───────────────┴───────────────┴──────────┘
                        ↓
              [Response Generator]
              (synthesizes all results)
                        ↓
                 Final Response
```

**Agents (Running in Parallel):**
1. **Sentiment Agent** - Analyzes sentiment, urgency, and emotions
2. **Knowledge Base Agent** - Searches docs, similar tickets, solutions
3. **Customer Context Agent** - Fetches profile, purchase history, subscription
4. **Status Agent** - Checks service status, known issues, outages
5. **Response Agent** - Synthesizes all results into final response

**Run:**
```bash
python 4_lg_multi_agent_async.py
# Server runs at http://0.0.0.0:8002
```

**Endpoints:**
- `POST /support/process` - Process ticket with parallel agent execution
- `GET /health` - Health check

**Request Schema:**
```json
{
  "id": "T-123",
  "customer_id": "C001",
  "message": "I can't login and it's urgent"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8002/support/process \
  -H "Content-Type: application/json" \
  -d '{
    "id": "T-123",
    "customer_id": "C001",
    "message": "I cannot login and it is very urgent!"
  }'
```

**Response Format:**
```json
{
  "ticket_id": "T-123",
  "response": "Generated support reply based on parallel analysis...",
  "metadata": {
    "sentiment": "Sentiment analysis results...",
    "solutions": "Recommended solutions...",
    "customer_context": "Customer profile and history...",
    "system_status": "Current system status..."
  },
  "processing_time": "~3-4s (async) vs ~15s (sync)"
}
```

**Use Cases:**
- High-throughput support ticket triage
- When agents can work independently
- Batch ticket processing for backlogs
- Faster SLAs by parallelizing I/O-bound operations
- Production support systems with high volume

**Key Differences: Sync vs Async:**

| Aspect | Sync (Sequential) | Async (Parallel) |
|--------|------------------|------------------|
| **Execution** | One agent at a time | All agents simultaneously |
| **Dependencies** | Each step depends on previous | No dependencies between agents |
| **Latency** | ~12-15 seconds | ~3-4 seconds |
| **Use Case** | Learning, sequential reasoning | Production, high throughput |
| **Data Flow** | Accumulates forward | Aggregated at end |
| **Complexity** | Easier to debug | More efficient |

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

### Multi-Agent Synchronous Flow (Sequential Pipeline)
```
Support Ticket
    ↓
Orchestrator Agent
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Sentiment Agent                                 │
│         (analyzes message)                              │
│         Output: sentiment + emotion                     │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Urgency Agent                                   │
│         (uses: sentiment + message)                     │
│         Output: urgency level + priority                │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Knowledge Agent                                 │
│         (uses: urgency + message)                       │
│         Output: solutions + docs + similar tickets      │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Customer Context Agent                          │
│         (uses: knowledge + customer_id)                 │
│         Output: profile + history + subscription        │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: System Status Agent                             │
│         (uses: customer context)                        │
│         Output: service status + known issues           │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 6: Response Generation Agent                       │
│         (uses: ALL previous outputs)                    │
│         Output: Final personalized response             │
└──────────────────┬──────────────────────────────────────┘
                   ↓
            Final Response
```

**Key Characteristic:** Each step DEPENDS on previous step's output. Data flows forward sequentially.

### Multi-Agent Async Flow (Parallel Execution)
```
Support Ticket
    ↓
Async Orchestrator
    ↓
┌────────────────────────────────────────────────────────────────┐
│           asyncio.gather() - Parallel Execution                │
│                                                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────┐ │
│  │ Sentiment  │  │ Knowledge  │  │  Customer  │  │ Status  │ │
│  │   Agent    │  │    Agent   │  │   Context  │  │  Agent  │ │
│  │            │  │            │  │   Agent    │  │         │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └────┬────┘ │
└────────┼───────────────┼────────────────┼──────────────┼──────┘
         │               │                │              │
         └───────────────┴────────────────┴──────────────┘
                                ↓
                    ┌───────────────────────┐
                    │  Response Generator   │
                    │  (synthesizes all)    │
                    └───────────┬───────────┘
                                ↓
                         Final Response
```

**Key Characteristic:** All agents run SIMULTANEOUSLY with NO dependencies. Results are aggregated at the end.

## 🔧 API Endpoints

### Basic Agent (Port 8000)
- `POST /agent` - Process query with basic agent
- `GET /health` - Health check

### LangChain Agent (Port 8001)
- `POST /agent` - Process query with LangChain agent
- `GET /health` - Health check

### Sync Multi-Agent (Port 8001)
- `POST /support/process` - Process support ticket through sequential pipeline
- `GET /health` - Health check with agent list
- `GET /` - System information and pipeline documentation

### Async Multi-Agent (Port 8002)
- `POST /support/process` - Process support ticket with parallel execution
- `GET /health` - Health check with agent list

### Request/Response Schemas

**Basic/LangChain Agents:**
```json
// Request
{
  "query": "string"
}

// Response
{
  "answer": "string",
  "tool_used": "string | null",
  "tool_result": "object | null"
}
```

**Sync/Async Multi-Agent:**
```json
// Request
{
  "id": "T-12345",
  "customer_id": "C001",
  "message": "Support ticket message"
}

// Response (Sync)
{
  "ticket_id": "T-12345",
  "response": "Final response after 6-step pipeline",
  "metadata": {
    "customer_id": "C001",
    "processing_type": "synchronous_pipeline",
    "steps": 6,
    "message_count": 15
  }
}

// Response (Async)
{
  "ticket_id": "T-12345",
  "response": "Final response from parallel processing",
  "metadata": {
    "sentiment": "Sentiment analysis...",
    "solutions": "Recommended solutions...",
    "customer_context": "Customer info...",
    "system_status": "Status info..."
  },
  "processing_time": "~3-4s (async) vs ~15s (sync)"
}
```

## 🧪 Testing Examples

### Python Requests

**Basic/LangChain Agents:**
```python
import requests

response = requests.post(
    "http://localhost:8000/agent",
    json={"query": "What's 15 multiplied by 8?"}
)
print(response.json())
```

**Sync Multi-Agent (Sequential Pipeline):**
```python
import requests

response = requests.post(
    "http://localhost:8001/support/process",
    json={
        "id": "T-12345",
        "customer_id": "C001",
        "message": "I cannot login and it's urgent!"
    }
)
print(response.json())
```

**Async Multi-Agent (Parallel Execution):**
```python
import requests

response = requests.post(
    "http://localhost:8002/support/process",
    json={
        "id": "T-67890",
        "customer_id": "C002",
        "message": "Payment is failing repeatedly!"
    }
)
print(response.json())
```

### cURL Examples

**Sync Multi-Agent:**
```bash
# Critical urgency ticket
curl -X POST http://localhost:8001/support/process \
  -H "Content-Type: application/json" \
  -d '{
    "id": "T-100",
    "customer_id": "C001",
    "message": "System is down! This is urgent and critical!"
  }'

# Login issue
curl -X POST http://localhost:8001/support/process \
  -H "Content-Type: application/json" \
  -d '{
    "id": "T-101",
    "customer_id": "C001",
    "message": "Cannot login after password reset"
  }'
```

**Async Multi-Agent:**
```bash
# Payment issue
curl -X POST http://localhost:8002/support/process \
  -H "Content-Type: application/json" \
  -d '{
    "id": "T-200",
    "customer_id": "C002",
    "message": "My payment keeps getting declined"
  }'

# General inquiry
curl -X POST http://localhost:8002/support/process \
  -H "Content-Type: application/json" \
  -d '{
    "id": "T-201",
    "customer_id": "C001",
    "message": "How do I upgrade my subscription?"
  }'
```

**Health Checks:**
```bash
# Check sync agent
curl http://localhost:8001/health

# Check async agent
curl http://localhost:8002/health

# Get sync pipeline info
curl http://localhost:8001/
```

## 📚 Key Concepts Learned

### 1. Tool Calling / Function Calling
- LLMs decide when and which tools to use
- Tools extend LLM capabilities beyond text generation
- Structured input/output schemas for reliable execution

### 2. Agent Patterns
- **ReAct Loop**: Reasoning → Action → Observation → Repeat
- **Single Agent**: One model with multiple tools
- **Sequential Multi-Agent**: Agents execute in order, passing data forward
- **Parallel Multi-Agent**: Agents execute simultaneously, results aggregated

### 3. LangChain Abstractions
- `create_agent()` - Simplified agent creation
- `@tool` decorator - Easy tool definition
- Message-based state management
- Structured output with Pydantic models
- `invoke()` vs `ainvoke()` - Sync vs async execution

### 4. Dependency Patterns
- **Sequential Dependencies**: Each tool depends on previous tool's output
- **Independent Tools**: Tools can run in parallel with no dependencies
- **Context Accumulation**: Building up information through pipeline stages
- **Result Aggregation**: Combining parallel results into final output

### 5. Async Patterns
- `asyncio.gather()` - Parallel execution of multiple async tasks
- `return_exceptions=True` - Graceful error handling
- `async/await` syntax for non-blocking operations
- Latency optimization through parallelization

### 6. Production Considerations
- Environment-based configuration
- Error handling and validation
- FastAPI for production-ready APIs
- Modular code organization (utils/)
- Performance optimization (sync vs async)

## 🎯 When to Use Sync vs Async

### Use Synchronous Pipeline (3_lg_multi_agent_sync.py) When:

✅ **Learning & Understanding**
- You're learning about agent orchestration
- You want to understand tool dependencies
- You need to debug data flow between agents

✅ **Sequential Dependencies Required**
- Each step truly needs output from previous step
- Complex reasoning that builds upon previous analysis
- Context must accumulate through stages

✅ **Explainability & Debugging**
- Need clear visibility into each step
- Want to trace how data flows through pipeline
- Easier to debug issues at specific stages

✅ **Use Cases:**
- Educational projects and tutorials
- Complex decision trees with dependencies
- Situations where order matters (e.g., approval workflows)
- When you need deterministic step-by-step processing

### Use Async Parallel (4_lg_multi_agent_async.py) When:

✅ **Performance is Critical**
- Need to minimize latency
- Processing high volumes of requests
- I/O-bound operations (API calls, database queries)

✅ **Independent Operations**
- Agents/tools can work without each other's outputs
- No dependencies between different analyses
- Results can be aggregated at the end

✅ **Production Systems**
- High-throughput requirements
- Need to meet strict SLA requirements
- Want to maximize resource utilization

✅ **Use Cases:**
- Production support ticket systems
- Batch processing of independent items
- Real-time dashboards with multiple data sources
- Microservices architectures
- High-volume API services

### Performance Comparison

| Metric | Sync (Sequential) | Async (Parallel) |
|--------|-------------------|------------------|
| **Processing Time** | ~12-15 seconds | ~3-4 seconds |
| **Latency** | High (cumulative) | Low (max of any agent) |
| **Resource Usage** | One agent at a time | All agents simultaneously |
| **Complexity** | Lower | Higher |
| **Debugging** | Easier | More challenging |
| **Best For** | Learning, dependencies | Production, throughput |

### Quick Decision Guide

```
Do your tools depend on each other's outputs?
    ├─ YES → Use Sync (Sequential Pipeline)
    └─ NO → Is performance critical?
              ├─ YES → Use Async (Parallel)
              └─ NO → Use Sync (easier to understand)
```

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

1. **Start with `1_basic_agent.py`**
   - Understand raw Gemini SDK
   - See function calling mechanics
   - Learn request/response parsing
   - No abstractions - see how it really works

2. **Move to `2_lg-agent.py`**
   - LangChain abstractions
   - Simplified agent creation with `create_agent()`
   - Message-based workflows
   - Single agent with multiple tools

3. **Explore `3_lg_multi_agent_sync.py`**
   - Sequential pipeline architecture
   - Tool dependencies and data flow
   - Context accumulation through stages
   - Orchestrator pattern
   - **Key Learning:** How to chain tools where each depends on previous output

4. **Master `4_lg_multi_agent_async.py`**
   - Parallel execution patterns
   - Async/await syntax
   - `asyncio.gather()` for concurrency
   - Error resilience with `return_exceptions`
   - Performance optimization
   - **Key Learning:** When and how to run agents in parallel for high throughput

**Recommended Order:**
```
Basic → LangChain → Sync Multi-Agent → Async Multi-Agent
 (1)      (2)            (3)                  (4)
```

**What You'll Learn at Each Stage:**
- **Stage 1-2:** Foundation of agents and tools
- **Stage 3:** Sequential reasoning and dependency management
- **Stage 4:** Performance optimization and production patterns

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
