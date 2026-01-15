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
