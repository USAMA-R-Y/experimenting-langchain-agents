import os
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

# components
from utils.tools import get_weather, calculator

load_dotenv()

app = FastAPI()

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
    system_prompt=SystemMessage("""
    You are a helpful assistant with access to tools. Use them when needed.
    Don't go beyond the scope of available tools.
    """)
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
        state = agent_executor.invoke({"messages": [{"role": "user", "content": request.query}]})

        messages = state.get("messages", [])
        answer = messages[-1].content if messages else ""

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
        port=8001
    )
