def extract_text_from_message(message) -> str:
    """
    Safely extract text content from a message.
    Handles both string content and complex multi-part content structures.
    
    Args:
        message: A message object with a content attribute
        
    Returns:
        str: Extracted text content
        
    Examples:
        - String content: "Hello world" -> "Hello world"
        - List content: [{'type': 'text', 'text': 'Hello'}] -> "Hello"
        - Empty/None: -> ""
    """
    content = message.content
    
    # If content is already a string, return it
    if isinstance(content, str):
        return content
    
    # If content is a list of parts, extract text from text parts
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
            elif hasattr(part, "type") and part.type == "text":
                text_parts.append(getattr(part, "text", ""))
        return " ".join(text_parts)
    
    # Fallback: try to convert to string
    return str(content) if content else ""


def safe_extract_from_result(result, default: str = "Unable to retrieve") -> str:
    """
    Safely extract text from an agent result, handling exceptions and errors.
    
    This is particularly useful in async multi-agent scenarios where individual
    agents may fail without bringing down the entire pipeline.
    
    Args:
        result: The agent result (dict with 'messages') or an Exception
        default: Default message to return if extraction fails
        
    Returns:
        str: Extracted text or error message
        
    Examples:
        - Success: {'messages': [msg]} -> "extracted text"
        - Exception: Exception("error") -> "Unable to retrieve: error"
        - Bad format: {} -> "Unable to retrieve: KeyError"
    """
    if isinstance(result, Exception):
        return f"{default}: {str(result)}"
    
    try:
        return extract_text_from_message(result["messages"][-1])
    except (KeyError, IndexError, TypeError) as e:
        return f"{default}: {str(e)}"


# ==================== GEMINI SDK HELPERS ====================

def extract_function_call_from_response(response):
    """
    Extract function call from Gemini SDK response.
    
    Used with native google.generativeai SDK (not LangChain).
    
    Args:
        response: Gemini GenerateContentResponse object
        
    Returns:
        FunctionCall object if present, None otherwise
        
    Example:
        >>> response = model.generate_content("What is 2+2?")
        >>> func_call = extract_function_call_from_response(response)
        >>> if func_call:
        ...     print(func_call.name, func_call.args)
    """
    return next(
        (
            part.function_call
            for candidate in response.candidates or []
            for part in (candidate.content.parts if candidate.content else [])
            if getattr(part, "function_call", None)
        ),
        None,
    )


def extract_text_from_response(response):
    """
    Extract text content from Gemini SDK response.
    
    Used with native google.generativeai SDK (not LangChain).
    
    Args:
        response: Gemini GenerateContentResponse object
        
    Returns:
        str: Extracted text or None if no text found
        
    Example:
        >>> response = model.generate_content("Hello")
        >>> text = extract_text_from_response(response)
        >>> print(text)
        "Hi! How can I help you?"
    """
    return next(
        (
            part.text
            for candidate in response.candidates or []
            for part in (candidate.content.parts if candidate.content else [])
            if getattr(part, "text", None)
        ),
        None,
    )
