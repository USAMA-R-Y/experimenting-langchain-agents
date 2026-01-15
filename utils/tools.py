from typing import List
from langchain_core.tools import tool

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
    """Gets current weather for a city

    Args:
        city: City name
    """
    weather_db = {
        "london": {"temp": 15, "condition": "Rainy", "humidity": 80},
        "paris": {"temp": 18, "condition": "Sunny", "humidity": 60},
        "new york": {"temp": 22, "condition": "Cloudy", "humidity": 70},
        "tokyo": {"temp": 25, "condition": "Clear", "humidity": 55}
    }
    return weather_db.get(city.lower(), {"temp": 20, "condition": "Unknown", "humidity": 65})


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