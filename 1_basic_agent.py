import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import os
from typing import Optional

from utils.helpers import extract_function_call_from_response, extract_text_from_response

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY is not set in the environment. "
        "Please create a .env file with GOOGLE_API_KEY=your_key_here"
    )

genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI(
    title="Basic Agent - Native Gemini SDK",
    version="1.0.0",
    description="Simple agent using native Google Gemini SDK with function calling"
)

# Tool definitions
TOOLS = [
    {
        "name": "calculator",
        "description": "Performs basic math operations (add, subtract, multiply, divide)",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The math operation to perform"
                },
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            },
            "required": ["operation", "a", "b"]
        }
    },
    {
        "name": "get_weather",
        "description": "Gets current weather for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    }
]

# Gemini expects function_declarations under a tool spec
FUNCTION_DECLARATIONS = [
    {
        "name": tool["name"],
        "description": tool["description"],
        "parameters": tool["input_schema"],
    }
    for tool in TOOLS
]


# Tool implementations
def calculator(operation: str, a: float, b: float) -> dict:
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
    }
    result = operations[operation](a, b)
    return {"result": result}


def get_weather(city: str) -> dict:
    # Mock weather data
    weather_db = {
        "london": {"temp": 15, "condition": "Rainy"},
        "paris": {"temp": 18, "condition": "Sunny"},
        "new york": {"temp": 22, "condition": "Cloudy"}
    }
    return weather_db.get(city.lower(), {"temp": 20, "condition": "Unknown"})


# Tool router
def execute_tool(tool_name: str, tool_input: dict) -> dict:
    if tool_name == "calculator":
        return calculator(**tool_input)
    elif tool_name == "get_weather":
        return get_weather(**tool_input)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


# Request/Response models
class QueryRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    answer: str
    tool_used: Optional[str] = None
    tool_result: Optional[dict] = None


@app.post("/agent", response_model=AgentResponse)
def agent_endpoint(request: QueryRequest):
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=[{"function_declarations": FUNCTION_DECLARATIONS}],
        system_instruction="You are a helpful assistant with access to tools. "
                          "Use the calculator for math operations and get_weather for weather queries. "
                          "Always provide clear and concise responses."
    )

    chat = model.start_chat(history=[])

    # Step 1: LLM decides whether to call a tool
    initial_response = chat.send_message(request.query)

    tool_used: Optional[str] = None
    tool_result: Optional[dict] = None

    function_call = extract_function_call_from_response(initial_response)

    if function_call:
        tool_name = function_call.name
        tool_input = dict(function_call.args or {})

        # Step 2: Execute the selected tool
        try:
            tool_result = execute_tool(tool_name, tool_input)
            tool_used = tool_name
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Tool execution failed: {str(e)}"
            )

        # Step 3: Provide tool output back to the model for the final answer
        follow_up = chat.send_message(
            {
                "function_response": {
                    "name": tool_name,
                    "response": tool_result,
                }
            }
        )

        answer = extract_text_from_response(follow_up) or "No response generated"
    else:
        # No tool needed, direct answer
        answer = extract_text_from_response(initial_response) or "No response generated"

    return AgentResponse(
        answer=answer,
        tool_used=tool_used,
        tool_result=tool_result
    )


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "2_lg_agent:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
