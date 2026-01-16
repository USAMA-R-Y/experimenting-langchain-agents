import os
from typing import List
import httpx

# libs
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

# ==================== TOOLS ====================

# Math Tools
@tool
def calculator(operation: str, a: float, b: float) -> dict:
    """Performs basic math operations (add, subtract, multiply, divide)

    Args:
        operation: The math operation (add, subtract, multiply, divide)
        a: First number
        b: Second number
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
    }
    result = operations[operation](a, b)
    return {"result": result}


@tool
def advanced_calculator(expression: str) -> dict:
    """Evaluates complex math expressions

    Args:
        expression: Math expression like "2**3 + 5*4"
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


# Weather Tools
@tool
def get_weather(city: str) -> dict:
    """Fetches the weather details for a city via WeatherAPI.

    Args:
        city: City name
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return {
            "error": "WEATHER_API_KEY not set",
            "message": "Create a .env with WEATHER_API_KEY from weatherapi.com",
        }

    url = "https://api.weatherapi.com/v1/current.json"
    params = {"q": city, "key": api_key}

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        return {
            "error": "Failed to fetch weather",
            "details": str(e),
            "city": city,
        }

    if "error" in data:
        return {
            "error": data["error"].get("message", "Unknown error"),
            "city": city,
        }

    location = data.get("location") or {}
    current = data.get("current") or {}
    condition = (current.get("condition") or {})

    return {
        "city": location.get("name"),
        "region": location.get("region"),
        "country": location.get("country"),
        "latitude": location.get("lat"),
        "longitude": location.get("lon"),
        "timezone": location.get("tz_id"),
        "localtime": location.get("localtime"),
        "temperature_c": current.get("temp_c"),
        "temperature_f": current.get("temp_f"),
        "is_day": current.get("is_day"),
        "condition": {
            "text": condition.get("text"),
            "icon": condition.get("icon"),
            "code": condition.get("code"),
        },
        "humidity": current.get("humidity"),
        "wind_kph": current.get("wind_kph"),
        "wind_dir": current.get("wind_dir"),
        "pressure_mb": current.get("pressure_mb"),
        "precip_mm": current.get("precip_mm"),
        "cloud": current.get("cloud"),
        "feelslike_c": current.get("feelslike_c"),
        "feelslike_f": current.get("feelslike_f"),
        "uv": current.get("uv"),
        "raw": data,
    }


@tool
def get_forecast(city: str, days: int) -> dict:
    """Gets weather forecast for upcoming days

    Args:
        city: City name
        days: Number of days (1-7)
    """
    forecasts = {
        "london": ["Rainy", "Cloudy", "Sunny", "Rainy", "Cloudy", "Sunny", "Rainy"],
        "paris": ["Sunny", "Sunny", "Cloudy", "Rainy", "Sunny", "Sunny", "Cloudy"],
        "new york": ["Cloudy", "Rainy", "Sunny", "Sunny", "Cloudy", "Rainy", "Sunny"],
        "tokyo": ["Clear", "Clear", "Cloudy", "Rainy", "Clear", "Clear", "Sunny"]
    }
    city_forecast = forecasts.get(city.lower(), ["Unknown"] * 7)
    return {"city": city, "forecast": city_forecast[:days]}


# Data Analysis Tools
@tool
def analyze_data(data: List[float]) -> dict:
    """Analyzes numerical data and returns statistics

    Args:
        data: List of numbers
    """
    if not data:
        return {"error": "Empty data"}

    return {
        "count": len(data),
        "sum": sum(data),
        "average": sum(data) / len(data),
        "min": min(data),
        "max": max(data)
    }


@tool
def filter_data(data: List[float], threshold: float, operation: str) -> dict:
    """Filters data based on threshold

    Args:
        data: List of numbers
        threshold: Threshold value
        operation: Operation (greater, less, equal)
    """
    operations = {
        "greater": lambda x: x > threshold,
        "less": lambda x: x < threshold,
        "equal": lambda x: x == threshold
    }
    filtered = [x for x in data if operations[operation](x)]
    return {"filtered_data": filtered, "count": len(filtered)}


# Text Tools
@tool
def text_analyzer(text: str) -> dict:
    """Analyzes text and returns statistics

    Args:
        text: Text to analyze
    """
    words = text.split()
    return {
        "character_count": len(text),
        "word_count": len(words),
        "sentence_count": text.count('.') + text.count('!') + text.count('?'),
        "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
    }


@tool
def search_database(query: str) -> dict:
    """Searches mock database for information

    Args:
        query: Search query
    """
    database = {
        "users": [
            {"id": 1, "name": "Alice", "role": "Admin"},
            {"id": 2, "name": "Bob", "role": "User"},
            {"id": 3, "name": "Charlie", "role": "Manager"}
        ],
        "products": [
            {"id": 1, "name": "Laptop", "price": 1200},
            {"id": 2, "name": "Phone", "price": 800},
            {"id": 3, "name": "Tablet", "price": 500}
        ]
    }
    query_lower = query.lower()

    if "user" in query_lower:
        return {"results": database["users"]}
    elif "product" in query_lower:
        return {"results": database["products"]}
    else:
        return {"results": []}


# ==================== SUPPORT TICKET TOOLS ====================

# Sentiment Analysis Tools
@tool
def analyze_sentiment(message: str) -> dict:
    """Analyzes sentiment of customer message

    Args:
        message: Customer message text
    """
    # Mock sentiment analysis based on keywords
    negative_keywords = ["angry", "frustrated", "terrible", "worst", "horrible", "broken", "useless"]
    positive_keywords = ["great", "excellent", "thanks", "happy", "love", "perfect", "amazing"]
    
    message_lower = message.lower()
    negative_count = sum(1 for word in negative_keywords if word in message_lower)
    positive_count = sum(1 for word in positive_keywords if word in message_lower)
    
    if negative_count > positive_count:
        sentiment = "negative"
        score = -0.7
    elif positive_count > negative_count:
        sentiment = "positive"
        score = 0.8
    else:
        sentiment = "neutral"
        score = 0.0
    
    return {
        "sentiment": sentiment,
        "score": score,
        "confidence": 0.85
    }


@tool
def detect_urgency(message: str) -> dict:
    """Detects urgency level of support ticket

    Args:
        message: Customer message text
    """
    urgent_keywords = ["urgent", "asap", "immediately", "emergency", "critical", "now", "broken"]
    message_lower = message.lower()
    
    urgent_count = sum(1 for word in urgent_keywords if word in message_lower)
    
    if urgent_count >= 2:
        level = "critical"
        priority = 1
    elif urgent_count == 1:
        level = "high"
        priority = 2
    else:
        level = "normal"
        priority = 3
    
    return {
        "urgency_level": level,
        "priority": priority,
        "requires_escalation": level == "critical"
    }


@tool
def classify_emotion(message: str) -> dict:
    """Classifies primary emotion in customer message

    Args:
        message: Customer message text
    """
    emotion_patterns = {
        "anger": ["angry", "furious", "mad", "outraged"],
        "frustration": ["frustrated", "annoyed", "irritated"],
        "sadness": ["disappointed", "sad", "unhappy"],
        "fear": ["worried", "concerned", "afraid"],
        "joy": ["happy", "excited", "thrilled", "delighted"]
    }
    
    message_lower = message.lower()
    emotion_scores = {}
    
    for emotion, keywords in emotion_patterns.items():
        score = sum(1 for word in keywords if word in message_lower)
        if score > 0:
            emotion_scores[emotion] = score
    
    if emotion_scores:
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        intensity = min(emotion_scores[primary_emotion] * 0.3, 1.0)
    else:
        primary_emotion = "neutral"
        intensity = 0.0
    
    return {
        "primary_emotion": primary_emotion,
        "intensity": intensity,
        "all_emotions": emotion_scores
    }


# Knowledge Base Tools
@tool
def search_docs(query: str) -> dict:
    """Searches documentation and help articles

    Args:
        query: Search query
    """
    # Mock knowledge base
    docs = {
        "login": {
            "title": "Login Issues",
            "summary": "Reset password via email or contact support",
            "url": "/docs/login-help",
            "relevance": 0.95
        },
        "payment": {
            "title": "Payment Problems",
            "summary": "Check card details, billing address, or try another payment method",
            "url": "/docs/payment-issues",
            "relevance": 0.90
        },
        "bug": {
            "title": "Report a Bug",
            "summary": "Submit bug report with screenshots and steps to reproduce",
            "url": "/docs/bug-report",
            "relevance": 0.85
        }
    }
    
    query_lower = query.lower()
    results = []
    
    for key, doc in docs.items():
        if key in query_lower or any(word in query_lower for word in doc["title"].lower().split()):
            results.append(doc)
    
    return {
        "results": results[:3] if results else [docs["bug"]],
        "total_found": len(results)
    }


@tool
def find_similar_tickets(description: str) -> dict:
    """Finds similar past support tickets

    Args:
        description: Ticket description
    """
    # Mock similar tickets database
    similar_tickets = [
        {
            "id": "T-1234",
            "issue": "Cannot login after password reset",
            "resolution": "Cleared browser cache and cookies",
            "resolved_time": "2 hours",
            "similarity": 0.87
        },
        {
            "id": "T-5678",
            "issue": "Payment declined with valid card",
            "resolution": "Updated billing address to match card",
            "resolved_time": "1 hour",
            "similarity": 0.72
        }
    ]
    
    # Mock matching logic
    if "login" in description.lower() or "password" in description.lower():
        return {"similar_tickets": [similar_tickets[0]], "count": 1}
    elif "payment" in description.lower():
        return {"similar_tickets": [similar_tickets[1]], "count": 1}
    else:
        return {"similar_tickets": similar_tickets[:1], "count": 1}


@tool
def get_solution_steps(issue_type: str) -> dict:
    """Gets step-by-step solution for common issues

    Args:
        issue_type: Type of issue (login, payment, bug, etc.)
    """
    solutions = {
        "login": {
            "steps": [
                "Clear browser cache and cookies",
                "Try incognito/private mode",
                "Reset password via email link",
                "Check for browser extensions blocking scripts"
            ],
            "estimated_time": "5-10 minutes",
            "success_rate": 0.92
        },
        "payment": {
            "steps": [
                "Verify card details are correct",
                "Check billing address matches card",
                "Try a different payment method",
                "Contact your bank for authorization"
            ],
            "estimated_time": "10-15 minutes",
            "success_rate": 0.88
        },
        "default": {
            "steps": [
                "Restart the application",
                "Check internet connection",
                "Update to latest version",
                "Contact support with error details"
            ],
            "estimated_time": "10 minutes",
            "success_rate": 0.75
        }
    }
    
    return solutions.get(issue_type.lower(), solutions["default"])


# Customer Context Tools
@tool
def get_customer_profile(customer_id: str) -> dict:
    """Retrieves customer profile information

    Args:
        customer_id: Customer ID
    """
    # Mock customer profiles
    profiles = {
        "C001": {
            "name": "John Doe",
            "email": "john@example.com",
            "account_type": "Premium",
            "member_since": "2023-01-15",
            "total_tickets": 3,
            "satisfaction_score": 4.5
        },
        "C002": {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "account_type": "Basic",
            "member_since": "2024-06-20",
            "total_tickets": 1,
            "satisfaction_score": 5.0
        }
    }
    
    return profiles.get(customer_id, {
        "name": "Unknown Customer",
        "email": "unknown@example.com",
        "account_type": "Basic",
        "member_since": "2024-01-01",
        "total_tickets": 0,
        "satisfaction_score": 0.0
    })


@tool
def fetch_purchase_history(customer_id: str) -> dict:
    """Fetches customer's purchase history

    Args:
        customer_id: Customer ID
    """
    # Mock purchase history
    history = {
        "C001": {
            "total_purchases": 5,
            "total_spent": 249.95,
            "last_purchase": "2024-12-15",
            "products": ["Premium Plan", "Add-on Pack", "Storage Upgrade"]
        },
        "C002": {
            "total_purchases": 1,
            "total_spent": 9.99,
            "last_purchase": "2024-11-20",
            "products": ["Basic Plan"]
        }
    }
    
    return history.get(customer_id, {
        "total_purchases": 0,
        "total_spent": 0.0,
        "last_purchase": None,
        "products": []
    })


@tool
def check_subscription_status(customer_id: str) -> dict:
    """Checks customer's subscription status

    Args:
        customer_id: Customer ID
    """
    # Mock subscription data
    subscriptions = {
        "C001": {
            "plan": "Premium",
            "status": "active",
            "renewal_date": "2025-02-15",
            "payment_method": "Credit Card ***1234",
            "auto_renew": True
        },
        "C002": {
            "plan": "Basic",
            "status": "active",
            "renewal_date": "2025-01-20",
            "payment_method": "PayPal",
            "auto_renew": True
        }
    }
    
    return subscriptions.get(customer_id, {
        "plan": "None",
        "status": "inactive",
        "renewal_date": None,
        "payment_method": None,
        "auto_renew": False
    })


# Product/Service Status Tools
@tool
def check_service_status() -> dict:
    """Checks current status of all services"""
    return {
        "overall_status": "operational",
        "services": {
            "api": {"status": "operational", "uptime": 99.9},
            "web_app": {"status": "operational", "uptime": 99.8},
            "database": {"status": "operational", "uptime": 99.95},
            "payment_gateway": {"status": "operational", "uptime": 99.7}
        },
        "last_incident": "2024-12-10",
        "next_maintenance": "2025-01-20"
    }


@tool
def get_known_issues() -> dict:
    """Retrieves list of known issues"""
    return {
        "issues": [
            {
                "id": "I-101",
                "title": "Slow dashboard loading on mobile",
                "severity": "low",
                "status": "investigating",
                "affected_users": "~5%",
                "reported": "2025-01-14"
            },
            {
                "id": "I-102",
                "title": "Email notifications delayed",
                "severity": "medium",
                "status": "fix_in_progress",
                "affected_users": "~2%",
                "reported": "2025-01-15",
                "eta": "2025-01-17"
            }
        ],
        "total_issues": 2
    }


@tool
def check_outages() -> dict:
    """Checks for any current service outages"""
    return {
        "active_outages": [],
        "recent_outages": [
            {
                "service": "API",
                "duration": "15 minutes",
                "occurred": "2025-01-10 14:30 UTC",
                "resolved": "2025-01-10 14:45 UTC",
                "impact": "API requests failed for some users"
            }
        ],
        "total_active": 0,
        "all_systems_operational": True
    }


# Response Generation Tools
@tool
def generate_response(context: str) -> dict:
    """Generates appropriate response based on context

    Args:
        context: Aggregated context from other agents
    """
    # This would typically use an LLM, but we'll return a template
    return {
        "response_template": "Thank you for contacting support. Based on your issue, here are the recommended steps...",
        "tone": "professional and empathetic",
        "estimated_resolution_time": "within 24 hours"
    }


@tool
def apply_tone_guidelines(message: str, sentiment: str) -> dict:
    """Applies appropriate tone based on customer sentiment

    Args:
        message: Draft response message
        sentiment: Customer sentiment (positive, negative, neutral)
    """
    tone_adjustments = {
        "negative": {
            "tone": "empathetic and apologetic",
            "opening": "We sincerely apologize for the inconvenience.",
            "closing": "We're committed to resolving this as quickly as possible."
        },
        "positive": {
            "tone": "friendly and appreciative",
            "opening": "Thank you for reaching out!",
            "closing": "We're here if you need anything else!"
        },
        "neutral": {
            "tone": "professional and helpful",
            "opening": "Thank you for contacting us.",
            "closing": "Please let us know if you have any questions."
        }
    }
    
    adjustment = tone_adjustments.get(sentiment, tone_adjustments["neutral"])
    
    return {
        "adjusted_message": f"{adjustment['opening']} {message} {adjustment['closing']}",
        "tone_applied": adjustment["tone"]
    }


@tool
def suggest_next_steps(issue_type: str, resolution_status: str) -> dict:
    """Suggests next steps for customer or support team

    Args:
        issue_type: Type of issue
        resolution_status: Current resolution status
    """
    next_steps = {
        "resolved": {
            "customer": ["Mark ticket as resolved", "Provide feedback"],
            "support": ["Follow up in 48 hours", "Close ticket"]
        },
        "pending": {
            "customer": ["Try suggested solutions", "Provide additional information"],
            "support": ["Monitor progress", "Escalate if not resolved in 24h"]
        },
        "escalated": {
            "customer": ["Wait for specialist contact", "Check email for updates"],
            "support": ["Assign to specialist", "Set priority to high"]
        }
    }
    
    return {
        "next_steps": next_steps.get(resolution_status, next_steps["pending"]),
        "follow_up_required": resolution_status != "resolved",
        "estimated_timeline": "24-48 hours"
    }