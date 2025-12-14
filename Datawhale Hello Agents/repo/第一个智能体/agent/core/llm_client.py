"""
Unified LLM Client Wrapper

This module provides a unified interface for interacting with various LLM providers
(OpenAI, Anthropic, Qwen, Zhipu, DeepSeek, Moonshot, etc.).

It handles:
1. Environment variable loading
2. Client initialization (with fault tolerance)
3. Transparent proxying based on model names
4. Unified text generation interface
5. Unified multimodal (image) interface
"""

import os
import base64
import mimetypes
from typing import Optional, Tuple
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# ============================================================================
# 1. Initialization & Configuration
# ============================================================================

load_dotenv()

# API Keys
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
qwen_api_key = os.getenv("QWEN_API_KEY")
zhipu_api_key = os.getenv("ZHIPU_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
moonshot_api_key = os.getenv("MOONSHOT_API_KEY")

# Base URLs
qwen_base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
zhipu_base_url = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
moonshot_base_url = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")

# Client Initialization (Fault Tolerant)
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
qwen_client = OpenAI(api_key=qwen_api_key, base_url=qwen_base_url) if qwen_api_key else None
zhipu_client = OpenAI(api_key=zhipu_api_key, base_url=zhipu_base_url) if zhipu_api_key else None
deepseek_client = OpenAI(api_key=deepseek_api_key, base_url=deepseek_base_url) if deepseek_api_key else None
kimi_client = OpenAI(api_key=moonshot_api_key, base_url=moonshot_base_url) if moonshot_api_key else None


# ============================================================================
# 2. Client Management (Transparent Proxy)
# ============================================================================

def get_client_for_model(model: str) -> Optional[OpenAI]:
    """
    Returns the appropriate OpenAI-compatible client based on the model name.
    
    Args:
        model: Model name (e.g., "qwen3-max", "glm-4v", "deepseek-chat")
    
    Returns:
        The corresponding OpenAI client, or None if not configured.
    """
    model_lower = model.lower()
    
    if "qwen" in model_lower:
        return qwen_client
    elif "glm" in model_lower:
        return zhipu_client
    elif "deepseek" in model_lower:
        return deepseek_client
    elif "kimi" in model_lower or "moonshot" in model_lower:
        return kimi_client
    else:
        return openai_client


def check_api_keys():
    """
    Prints the configuration status of API keys for debugging.
    """
    keys_status = {
        "OpenAI": "✅" if openai_api_key else "❌",
        "Anthropic": "✅" if anthropic_api_key else "❌",
        "Qwen": "✅" if qwen_api_key else "❌",
        "Zhipu": "✅" if zhipu_api_key else "❌",
        "DeepSeek": "✅" if deepseek_api_key else "❌",
        "Moonshot": "✅" if moonshot_api_key else "❌",
    }
    
    print("🔑 API Keys Configuration Status:")
    for provider, status in keys_status.items():
        print(f"  {status} {provider}")
    print()


# ============================================================================
# 3. Unified Text Generation
# ============================================================================

def get_response(model: str, prompt: str, temperature: float = 0) -> str:
    """
    Unified interface for text generation across all providers.
    
    Args:
        model: Model name
        prompt: User prompt
        temperature: Temperature (0-1)
    
    Returns:
        Generated text content
    """
    if "claude" in model.lower() or "anthropic" in model.lower():
        # Anthropic Claude API
        if not anthropic_client:
            return f"Error: Anthropic client not initialized. Check ANTHROPIC_API_KEY."
        
        message = anthropic_client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=temperature,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
        return message.content[0].text
    
    else:
        # OpenAI Compatible API
        client = get_client_for_model(model)
        if not client:
            return f"Error: Client for model '{model}' not initialized. Check API keys in .env file."
        
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


# ============================================================================
# 4. Unified Multimodal (Image) Generation
# ============================================================================

def encode_image_b64(path: str) -> Tuple[str, str]:
    """
    Encodes an image file to Base64.
    
    Args:
        path: Path to the image file
    
    Returns:
        (media_type, base64_string)
    """
    mime, _ = mimetypes.guess_type(path)
    media_type = mime or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return media_type, b64


def image_anthropic_call(model_name: str, prompt: str, media_type: str, b64: str) -> str:
    """
    Calls Anthropic's multimodal API.
    """
    if not anthropic_client:
        return "Error: Anthropic client not initialized."
    
    msg = anthropic_client.messages.create(
        model=model_name,
        max_tokens=2000,
        temperature=0,
        system=(
            "You are a careful assistant. Respond with a single valid JSON object only. "
            "Do not include markdown, code fences, or commentary outside JSON."
        ),
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            ],
        }],
    )
    
    parts = []
    for block in (msg.content or []):
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "".join(parts).strip()


def image_openai_call(model_name: str, prompt: str, media_type: str, b64: str) -> str:
    """
    Calls OpenAI-compatible multimodal API (GPT-4V, Qwen-VL, GLM-4V).
    """
    client = get_client_for_model(model_name)
    if not client:
        return f"Error: Client for model '{model_name}' not initialized."
    
    data_url = f"data:{media_type};base64,{b64}"
    resp = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    )
    content = resp.choices[0].message.content
    return (content or "").strip()
