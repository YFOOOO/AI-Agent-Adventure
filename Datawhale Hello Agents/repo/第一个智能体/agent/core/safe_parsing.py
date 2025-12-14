"""
Safe Parsing Utilities

This module provides robust functions for parsing and cleaning LLM outputs.
It handles common issues like Markdown code fences, missing tags, and JSON formatting.
"""

import re
from typing import Optional

def ensure_execute_python_tags(text: str) -> str:
    """
    Normalizes LLM generated code by ensuring it is wrapped in <execute_python> tags.
    
    Steps:
    1. Removes Markdown code fences (```python ... ```)
    2. Adds <execute_python> tags if missing
    
    Args:
        text: Raw text from LLM
    
    Returns:
        Normalized text with <execute_python> tags
    """
    text = text.strip()
    
    # Remove Markdown code fences
    text = re.sub(r"^```(?:python)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    
    # Add tags if missing
    if "<execute_python>" not in text:
        text = f"<execute_python>\n{text}\n</execute_python>"
    
    return text


def extract_code_from_tags(text: str) -> Optional[str]:
    """
    Extracts code from <execute_python> tags.
    
    Args:
        text: Text containing tags
    
    Returns:
        Extracted code string, or None if not found
    """
    match = re.search(r"<execute_python>(.*?)</execute_python>", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None
