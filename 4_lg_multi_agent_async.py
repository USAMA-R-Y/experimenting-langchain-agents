import asyncio
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import SystemMessage

# Import tools
from utils.tools import (
    # Sentiment tools
    analyze_sentiment, detect_urgency, classify_emotion,
    # Knowledge base tools
    search_docs, find_similar_tickets, get_solution_steps,
    # Customer context tools
    get_customer_profile, fetch_purchase_history, check_subscription_status,
    # Status tools
    check_service_status, get_known_issues, check_outages,
    # Response tools
    generate_response, apply_tone_guidelines, suggest_next_steps
)
from utils.helpers import extract_text_from_message, safe_extract_from_result

load_dotenv()

app = FastAPI(title="Async Multi-Agent Support System", version="1.0.0")


# ==================== PYDANTIC MODELS ====================

class TicketRequest(BaseModel):
    id: str
    customer_id: str
    message: str


class SupportResponse(BaseModel):
    ticket_id: str
    response: str
    metadata: Dict[str, str]
    processing_time: str


# ==================== SPECIALIZED AGENTS ====================

def create_llm():
    """Create configured LLM instance"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )


# 1. Sentiment Analysis Agent
sentiment_agent = create_agent(
    create_llm(),
    tools=[analyze_sentiment, detect_urgency, classify_emotion],
    system_prompt=SystemMessage(content="Analyze customer sentiment and urgency from support messages.")
)

# 2. Knowledge Base Agent
kb_agent = create_agent(
    create_llm(),
    tools=[search_docs, find_similar_tickets, get_solution_steps],
    system_prompt=SystemMessage(content="Search knowledge base for relevant solutions and documentation.")
)

# 3. Customer Context Agent
context_agent = create_agent(
    create_llm(),
    tools=[get_customer_profile, fetch_purchase_history, check_subscription_status],
    system_prompt=SystemMessage(content="Retrieve customer context and history.")
)

# 4. Product Status Agent
status_agent = create_agent(
    create_llm(),
    tools=[check_service_status, get_known_issues, check_outages],
    system_prompt=SystemMessage(content="Check product/service health and known issues.")
)

# 5. Response Generation Agent
response_agent = create_agent(
    create_llm(),
    tools=[generate_response, apply_tone_guidelines, suggest_next_steps],
    system_prompt=SystemMessage(content="Generate contextual, empathetic customer responses.")
)


# ==================== ASYNC ORCHESTRATOR ====================
async def process_ticket_parallel(ticket: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process support ticket with parallel agent execution.
    
    Benefits of async here:
    - All agents query external APIs/databases simultaneously
    - Reduce total latency from ~15s (sequential) to ~3-4s (parallel)
    - Better resource utilization
    """

    ticket_text = ticket["message"]
    customer_id = ticket["customer_id"]

    # Launch all agents concurrently
    results = await asyncio.gather(
        # Each agent runs independently
        sentiment_agent.ainvoke({
            "messages": [{"role": "user", "content": f"Analyze: {ticket_text}"}]
        }),

        kb_agent.ainvoke({
            "messages": [{"role": "user", "content": f"Find solutions for: {ticket_text}"}]
        }),

        context_agent.ainvoke({
            "messages": [{"role": "user", "content": f"Get context for customer: {customer_id}"}]
        }),

        status_agent.ainvoke({
            "messages": [{"role": "user", "content": "Check current service status"}]
        }),

        return_exceptions=True  # Don't fail entire pipeline if one agent fails
    )

    # Unpack results and handle potential exceptions
    sentiment_result, kb_result, context_result, status_result = results

    # Aggregate insights using safe extraction helper
    aggregated_context = {
        "sentiment": safe_extract_from_result(sentiment_result, "Sentiment analysis unavailable"),
        "solutions": safe_extract_from_result(kb_result, "Solutions unavailable"),
        "customer_context": safe_extract_from_result(context_result, "Customer context unavailable"),
        "system_status": safe_extract_from_result(status_result, "Status check unavailable"),
    }

    # Final agent synthesizes everything into a response
    final_response = await response_agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": f"""
            Generate support response using:
            
            Original Ticket: {ticket_text}
            Sentiment Analysis: {aggregated_context['sentiment']}
            Recommended Solutions: {aggregated_context['solutions']}
            Customer Context: {aggregated_context['customer_context']}
            System Status: {aggregated_context['system_status']}
            """
        }]
    })

    return {
        "ticket_id": ticket["id"],
        "response": extract_text_from_message(final_response["messages"][-1]),
        "metadata": aggregated_context,
        "processing_time": "~3-4s (async) vs ~15s (sync)"
    }


# ==================== FASTAPI ENDPOINT ====================

@app.post("/support/process")
async def process_support_ticket(ticket: TicketRequest):
    """
    Async endpoint that handles concurrent agent execution.
    """
    try:
        result = await process_ticket_parallel(ticket.dict())
        return SupportResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "async-multi-agent-support",
        "agents": ["sentiment", "knowledge_base", "customer_context", "status", "response_generation"]
    }


if __name__ == "__main__":
    uvicorn.run(
        "4_lg_multi_agent_async:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
    )
