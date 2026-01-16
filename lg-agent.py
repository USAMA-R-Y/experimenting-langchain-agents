import os
from uuid import uuid4
from typing import Optional
import uvicorn
from dotenv import load_dotenv

# libs
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# lg
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

# components
from utils.tools import get_weather, calculator
from utils.helpers import extract_text_from_message

load_dotenv()

# Validate API key
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError(
        "GOOGLE_API_KEY is not set in the environment. "
        "Please create a .env file with GOOGLE_API_KEY=your_key_here"
    )

app = FastAPI(
    title="LangChain Agent - Single Agent",
    version="1.0.0",
    description="Simple LangChain agent with calculator and weather tools"
)

# Initialize LLM
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

# Create agent (use prompt=... in 0.3)
agent_executor = create_agent(
    model,
    tools=[calculator, get_weather],
    checkpointer=InMemorySaver(),
    system_prompt=SystemMessage(content="You are a helpful assistant with access to tools. "
                                        "Use the calculator for math operations and get_weather for weather information. "
                                        "Don't go beyond the scope of available tools.")
)


# Request/Response models
class QueryRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    answer: str
    intermediate_steps: Optional[list] = None


@app.post("/agent", response_model=AgentResponse)
def agent_endpoint(request: QueryRequest):
    try:
        state = agent_executor.invoke(
            {"messages": [{"role": "user", "content": request.query}]},
            {"configurable": {"thread_id": str(uuid4())}},
        )

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
        "lg-agent:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
