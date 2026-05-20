"""LLM abstraction layer — supports OpenAI and Anthropic Claude."""
from typing import List
from openai import OpenAI
import anthropic

from backend.config import get_settings

settings = get_settings()
_openai = OpenAI(api_key=settings.openai_api_key)
_anthropic = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def chat(messages: List[dict], json_mode: bool = False) -> str:
    """
    Send messages to the configured LLM and return the text response.
    messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
    """
    if settings.llm_provider == "anthropic":
        return _chat_anthropic(messages)
    return _chat_openai(messages, json_mode=json_mode)


def _chat_openai(messages: List[dict], json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.chat_model,
        "messages": messages,
        "temperature": 0.2,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = _openai.chat.completions.create(**kwargs)
    return response.choices[0].message.content.strip()


def _chat_anthropic(messages: List[dict]) -> str:
    system_msg = ""
    filtered = []
    for m in messages:
        if m["role"] == "system":
            system_msg = m["content"]
        else:
            filtered.append({"role": m["role"], "content": m["content"]})

    response = _anthropic.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        system=system_msg,
        messages=filtered,
        temperature=0.2,
    )
    return response.content[0].text.strip()


def model_name() -> str:
    if settings.llm_provider == "anthropic":
        return "claude-opus-4-5"
    return settings.chat_model
