import os
import operator
from uuid import uuid4
import uvicorn
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence, Optional, Literal

# libs
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.messages import AnyMessage

# langchain & langgraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

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
    title="LangGraph Agent - Graph-Based Architecture",
    version="1.0.0",
    description="LangGraph agent with explicit graph structure, nodes, and edges"
)


# ==================== STATE DEFINITION ====================
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


# ==================== LLM INITIALIZATION ====================
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

# Bind tools to the model (enables function calling)
tools = [calculator, get_weather]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


# ==================== NODE FUNCTIONS ====================
def llm_call(state: dict):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }


def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END


# ==================== GRAPH CONSTRUCTION ====================
"""
Builds the LangGraph agent with explicit graph structure.

Graph Structure:

    START
      ↓
    agent (call_model)
      ↓
    [should_continue?]
      ↓           ↓
   tools        END
      ↓
    agent (loop back)

The graph implements a ReAct-style loop:
1. Agent thinks and decides on action
2. If tools needed, execute them
3. Feed results back to agent
4. Repeat until agent has final answer
"""
# Initialize the StateGraph with our state schema
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
agent = agent_builder.compile()


# ==================== API MODELS ====================
class QueryRequest(BaseModel):
    """Request model for agent queries"""
    query: str


class AgentResponse(BaseModel):
    """Response model with answer and metadata"""
    answer: str
    intermediate_steps: Optional[list] = None
    graph_steps: Optional[int] = None


# ==================== API ENDPOINTS ====================
@app.post("/agent", response_model=AgentResponse)
def agent_endpoint(request: QueryRequest):
    """
    Process a query through the LangGraph agent.
    
    The graph will:
    1. Receive the user's message
    2. Let the LLM decide on actions
    3. Execute any needed tools
    4. Loop until a final answer is ready
    5. Return the complete response
    """
    try:
        # Create initial state with user message
        initial_state = {
            "messages": [HumanMessage(content=request.query)]
        }

        # Run the graph with a unique thread ID for conversation tracking
        config = {"configurable": {"thread_id": str(uuid4())}}

        # Invoke the graph - it will run until reaching END
        final_state = agent.invoke(initial_state, config)

        # Extract the final answer from the last message
        messages = final_state.get("messages", [])
        answer = extract_text_from_message(messages[-1]) if messages else "No response generated"

        # Count the number of steps (messages) in the conversation
        graph_steps = len(messages)

        return AgentResponse(
            answer=answer,
            intermediate_steps=None,
            graph_steps=graph_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "agent_type": "langgraph",
        "graph_nodes": ["agent", "tools"],
        "description": "LangGraph agent with explicit state graph"
    }


@app.get("/")
def root():
    """Root endpoint with quick start guide"""
    return {
        "title": "LangGraph Agent API",
        "description": "A graph-based agent using LangGraph's StateGraph architecture",
        "features": [
            "Explicit graph structure with nodes and edges",
            "State-based conversation management",
            "ReAct-style reasoning loop",
            "Tool execution with automatic routing",
            "Memory checkpointing for conversation continuity"
        ],
        "endpoints": {
            "POST /agent": "Send a query to the agent",
            "GET /health": "Health check",
            "GET /graph-info": "Detailed graph structure information",
            "GET /": "This information"
        },
        "example_queries": [
            "What is 25 multiplied by 8?",
            "What's the weather in Tokyo?",
            "Calculate 2^10 and then tell me the weather in Paris"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "5_lgraph_agent:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )
