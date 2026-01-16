import os
from typing import Optional, List, Literal

# libs
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import uvicorn
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage
from langchain.tools import tool

# components
from utils.tools import calculator, advanced_calculator, analyze_data, filter_data, get_weather, get_forecast, \
    search_database, text_analyzer
from utils.helpers import extract_text_from_message

load_dotenv()

# Validate API key
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError(
        "GOOGLE_API_KEY is not set in the environment. "
        "Please create a .env file with GOOGLE_API_KEY=your_key_here"
    )

app = FastAPI(
    title="Multi-Agent System - Synchronous",
    version="1.0.0",
    description="Hierarchical multi-agent system with specialized agents for math, weather, and research"
)


# ==================== AGENTS ====================
def create_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )


# Math Agent
math_tools = [calculator, advanced_calculator, analyze_data, filter_data]
math_agent = create_agent(
    create_llm(),
    math_tools,
    system_prompt=SystemMessage(content="You are a math expert. Use your tools to solve mathematical problems and analyze numerical data.")
)


@tool("math_tool", description="Perform mathematical calculations")
def call_math_agent(query: str):
    result = math_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return extract_text_from_message(result["messages"][-1])


# Weather Agent
weather_tools = [get_weather, get_forecast]
weather_agent = create_agent(
    create_llm(),
    tools=weather_tools,
    system_prompt=SystemMessage(content="You are a weather specialist. Provide detailed weather information and forecasts.")
)


@tool("weather_tool", description="Return weather information")
def call_weather_agent(query: str):
    result = weather_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return extract_text_from_message(result["messages"][-1])


# Research Agent
research_tools = [search_database, text_analyzer]
research_agent = create_agent(
    create_llm(),
    tools=research_tools,
    system_prompt=SystemMessage(content="You are a research assistant. Search databases and analyze text to answer questions.")
)


@tool("research_tool", description="As a research assistant, Search databases and analyze text to answer questions.")
def call_research_agent(query: str):
    result = research_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return extract_text_from_message(result["messages"][-1])


# General Agent (has access to all tools)
all_tools = [call_math_agent, call_weather_agent, call_research_agent]
general_agent = create_agent(
    create_llm(),
    tools=all_tools,
    system_prompt=SystemMessage(content="You are a general assistant with access to multiple specialized agents. "
                                         "Choose the right agent tool for the task: math_tool for calculations, "
                                         "weather_tool for weather information, research_tool for database searches and text analysis.")
)


# ==================== API ====================
class QueryRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    answer: str
    intermediate_steps: Optional[list] = None


@app.post("/agent", response_model=AgentResponse)
def agent_endpoint(request: QueryRequest):
    try:
        # Invoke agent with LangChain 0.3 API
        state = general_agent.invoke({
            "messages": [{"role": "user", "content": request.query}]
        })

        # Extract answer from the last message
        messages = state.get("messages", [])
        answer = extract_text_from_message(messages[-1]) if messages else ""

        return AgentResponse(answer=answer, intermediate_steps=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "lg-multi-agent-sync:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
