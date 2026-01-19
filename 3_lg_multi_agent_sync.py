import os
from typing import Optional, Dict, Any
from uuid import uuid4

# libs
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import uvicorn
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import SystemMessage
from langchain.tools import tool

# components
from utils.tools import (
    analyze_sentiment,
    detect_urgency,
    classify_emotion,
    search_docs,
    find_similar_tickets,
    get_solution_steps,
    get_customer_profile,
    fetch_purchase_history,
    check_subscription_status,
    check_service_status,
    get_known_issues,
    generate_response,
    apply_tone_guidelines,
    suggest_next_steps
)
from utils.helpers import extract_text_from_message

load_dotenv()

# Validate API key
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError(
        "GOOGLE_API_KEY is not set in the environment. "
        "Please create a .env file with GOOGLE_API_KEY=your_key_here"
    )

app = FastAPI(
    title="Multi-Agent System - Synchronous with Tool Dependencies",
    version="2.0.0",
    description="Hierarchical multi-agent system where each agent's output feeds into the next agent"
)


# ==================== AGENTS WITH DEPENDENCIES ====================
def create_llm():
    """Create a configured LLM instance"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )


# ==================== STEP 1: SENTIMENT AGENT ====================
# This agent analyzes the emotional content of the customer message
sentiment_tools = [analyze_sentiment, classify_emotion]
sentiment_agent = create_agent(
    create_llm(),
    sentiment_tools,
    system_prompt=SystemMessage(
        content="You are a sentiment analysis expert. Analyze customer messages to understand "
                "their emotional state. Use analyze_sentiment to get overall sentiment and "
                "classify_emotion to understand specific emotions."
    )
)


@tool("sentiment_analysis_tool")
def call_sentiment_agent(message: str) -> str:
    """
    Analyzes the sentiment and emotion of a customer message.
    This is STEP 1 in the pipeline.
    
    Args:
        message: The customer's message text
    
    Returns:
        Sentiment analysis results including sentiment, emotion, and scores
    """
    result = sentiment_agent.invoke({"messages": [{"role": "user", "content": message}]})
    return extract_text_from_message(result["messages"][-1])


# ==================== STEP 2: URGENCY AGENT ====================
# This agent determines urgency based on the message AND sentiment from Step 1
urgency_tools = [detect_urgency]
urgency_agent = create_agent(
    create_llm(),
    urgency_tools,
    system_prompt=SystemMessage(
        content="You are an urgency detection expert. Analyze support tickets to determine "
                "their urgency level. Consider both the message content and any sentiment "
                "information provided to assess priority accurately."
    )
)


@tool("urgency_detection_tool")
def call_urgency_agent(message: str, sentiment_info: str) -> str:
    """
    Detects urgency level based on message content and sentiment analysis.
    This is STEP 2 - it DEPENDS on output from sentiment_analysis_tool.
    
    Args:
        message: The customer's message text
        sentiment_info: Sentiment analysis from previous step
    
    Returns:
        Urgency analysis including level, priority, and escalation needs
    """
    combined_context = f"Message: {message}\n\nSentiment Analysis: {sentiment_info}"
    result = urgency_agent.invoke({"messages": [{"role": "user", "content": combined_context}]})
    return extract_text_from_message(result["messages"][-1])


# ==================== STEP 3: KNOWLEDGE AGENT ====================
# This agent searches knowledge base based on message AND urgency from Step 2
knowledge_tools = [search_docs, find_similar_tickets, get_solution_steps]
knowledge_agent = create_agent(
    create_llm(),
    knowledge_tools,
    system_prompt=SystemMessage(
        content="You are a knowledge base expert. Search documentation, find similar past "
                "tickets, and retrieve solution steps. Use urgency information to prioritize "
                "the most relevant and effective solutions."
    )
)


@tool("knowledge_search_tool")
def call_knowledge_agent(message: str, urgency_info: str) -> str:
    """
    Searches knowledge base for solutions based on message and urgency.
    This is STEP 3 - it DEPENDS on output from urgency_detection_tool.
    
    Args:
        message: The customer's message text
        urgency_info: Urgency analysis from previous step
    
    Returns:
        Relevant documentation, similar tickets, and solution steps
    """
    combined_context = f"Message: {message}\n\nUrgency Info: {urgency_info}\n\nPlease search for relevant solutions."
    result = knowledge_agent.invoke({"messages": [{"role": "user", "content": combined_context}]})
    return extract_text_from_message(result["messages"][-1])


# ==================== STEP 4: CUSTOMER CONTEXT AGENT ====================
# This agent fetches customer info based on customer ID and previous insights
customer_tools = [get_customer_profile, fetch_purchase_history, check_subscription_status]
customer_agent = create_agent(
    create_llm(),
    customer_tools,
    system_prompt=SystemMessage(
        content="You are a customer context specialist. Retrieve comprehensive customer "
                "information including profile, purchase history, and subscription status. "
                "Use this to personalize the support experience."
    )
)


@tool("customer_context_tool")
def call_customer_agent(customer_id: str, knowledge_info: str) -> str:
    """
    Retrieves customer context based on ID and knowledge search results.
    This is STEP 4 - it DEPENDS on output from knowledge_search_tool.
    
    Args:
        customer_id: The customer's ID
        knowledge_info: Knowledge search results from previous step
    
    Returns:
        Customer profile, purchase history, and subscription details
    """
    combined_context = f"Customer ID: {customer_id}\n\nKnowledge Info: {knowledge_info}\n\nRetrieve full customer context."
    result = customer_agent.invoke({"messages": [{"role": "user", "content": combined_context}]})
    return extract_text_from_message(result["messages"][-1])


# ==================== STEP 5: SYSTEM STATUS AGENT ====================
# This agent checks system status to identify any ongoing issues
status_tools = [check_service_status, get_known_issues]
status_agent = create_agent(
    create_llm(),
    status_tools,
    system_prompt=SystemMessage(
        content="You are a system status monitor. Check current service status and known issues "
                "to determine if customer problems might be related to system-wide problems."
    )
)


@tool("system_status_tool")
def call_status_agent(customer_context: str) -> str:
    """
    Checks system status based on customer context and issue details.
    This is STEP 5 - it DEPENDS on output from customer_context_tool.
    
    Args:
        customer_context: Customer information from previous step
    
    Returns:
        Current system status and any known issues
    """
    combined_context = f"Customer Context: {customer_context}\n\nCheck if there are any system issues related to this customer."
    result = status_agent.invoke({"messages": [{"role": "user", "content": combined_context}]})
    return extract_text_from_message(result["messages"][-1])


# ==================== STEP 6: RESPONSE GENERATION AGENT ====================
# This agent creates final response using ALL previous outputs
response_tools = [generate_response, apply_tone_guidelines, suggest_next_steps]
response_agent = create_agent(
    create_llm(),
    response_tools,
    system_prompt=SystemMessage(
        content="You are a response generation expert. Create comprehensive, personalized support "
                "responses using all available context: sentiment, urgency, solutions, customer info, "
                "and system status. Apply appropriate tone and suggest clear next steps."
    )
)


@tool("response_generation_tool")
def call_response_agent(
    message: str,
    sentiment_info: str,
    urgency_info: str,
    knowledge_info: str,
    customer_context: str,
    system_status: str
) -> str:
    """
    Generates final response using ALL previous agent outputs.
    This is STEP 6 (FINAL) - it DEPENDS on ALL previous tools.
    
    Args:
        message: Original customer message
        sentiment_info: From Step 1
        urgency_info: From Step 2
        knowledge_info: From Step 3
        customer_context: From Step 4
        system_status: From Step 5
    
    Returns:
        Final personalized support response
    """
    full_context = f"""
Original Message: {message}

Sentiment Analysis: {sentiment_info}

Urgency Assessment: {urgency_info}

Knowledge & Solutions: {knowledge_info}

Customer Context: {customer_context}

System Status: {system_status}

Generate a comprehensive, personalized support response that addresses the customer's issue.
Apply appropriate tone based on sentiment and provide clear next steps based on urgency.
"""
    result = response_agent.invoke({"messages": [{"role": "user", "content": full_context}]})
    return extract_text_from_message(result["messages"][-1])


# ==================== ORCHESTRATOR AGENT ====================
# This agent coordinates the entire pipeline
all_tools = [
    call_sentiment_agent,
    call_urgency_agent,
    call_knowledge_agent,
    call_customer_agent,
    call_status_agent,
    call_response_agent
]

orchestrator_agent = create_agent(
    create_llm(),
    tools=all_tools,
    system_prompt=SystemMessage(
        content="""You are an orchestrator for a support ticket processing system.

You MUST follow this EXACT sequence to process tickets:

STEP 1: Use sentiment_analysis_tool with the customer message
STEP 2: Use urgency_detection_tool with the message AND sentiment results from Step 1
STEP 3: Use knowledge_search_tool with the message AND urgency results from Step 2
STEP 4: Use customer_context_tool with customer_id AND knowledge results from Step 3
STEP 5: Use system_status_tool with customer context from Step 4
STEP 6: Use response_generation_tool with ALL previous results (message, sentiment, urgency, knowledge, customer_context, system_status)

Each step DEPENDS on the previous step's output. Follow this sequence exactly and pass the accumulated context forward at each step.
"""
    )
)


# ==================== API ====================
class TicketRequest(BaseModel):
    """Support ticket request"""
    id: str
    customer_id: str
    message: str


class SupportResponse(BaseModel):
    """Support ticket response with processing details"""
    ticket_id: str
    response: str
    metadata: Dict[str, Any]


@app.post("/support/process", response_model=SupportResponse)
def process_ticket(request: TicketRequest):
    """
    Process a support ticket through the synchronous pipeline.
    Each agent's output feeds into the next agent as input.
    """
    try:
        # Prepare the orchestration query
        orchestration_query = f"""
Process this support ticket through all 6 steps in sequence:

Ticket ID: {request.id}
Customer ID: {request.customer_id}
Message: {request.message}

Follow the exact 6-step pipeline, passing outputs forward at each step.
"""
        
        # Invoke orchestrator
        state = orchestrator_agent.invoke(
            {"messages": [{"role": "user", "content": orchestration_query}]},
            {"configurable": {"thread_id": str(uuid4())}},
        )
        
        # Extract final response
        messages = state.get("messages", [])
        final_response = extract_text_from_message(messages[-1]) if messages else "No response generated"
        
        return SupportResponse(
            ticket_id=request.id,
            response=final_response,
            metadata={
                "customer_id": request.customer_id,
                "processing_type": "synchronous_pipeline",
                "steps": 6,
                "message_count": len(messages)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "system": "Multi-Agent Synchronous Pipeline",
        "agents": [
            "sentiment_agent",
            "urgency_agent", 
            "knowledge_agent",
            "customer_agent",
            "status_agent",
            "response_agent"
        ],
        "pipeline": "Each agent depends on previous agent's output"
    }


@app.get("/")
def root():
    """Root endpoint with system info"""
    return {
        "title": "Synchronous Multi-Agent Pipeline",
        "description": "A 6-step support ticket processing system where each tool depends on previous outputs",
        "pipeline_steps": [
            "1. Sentiment Analysis (analyze message)",
            "2. Urgency Detection (uses sentiment + message)",
            "3. Knowledge Search (uses urgency + message)",
            "4. Customer Context (uses knowledge + customer_id)",
            "5. System Status (uses customer context)",
            "6. Response Generation (uses ALL previous outputs)"
        ],
        "endpoints": {
            "/support/process": "POST - Process a support ticket",
            "/health": "GET - Health check",
            "/": "GET - This info"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "3_lg_multi_agent_sync:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
