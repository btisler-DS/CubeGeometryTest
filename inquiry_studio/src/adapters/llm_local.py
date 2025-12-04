import json
from typing import Tuple, Dict, Any

import requests

from ..studio_config import logger


# Adjust these if your LM Studio server uses different settings.
LMSTUDIO_BASE_URL = "http://localhost:1234/v1/chat/completions"

# Set this to the exact model identifier shown in LM Studio's server UI
LMSTUDIO_MODEL_ID = "Meta-Llama-3-8B-Instruct-GGUF"


def query_local_llm(question: str) -> Tuple[str, Dict[str, Any]]:
    """
    Call a local LM Studio server running Meta-Llama-3-8B-Instruct-GGUF
    (or another model) using the OpenAI-compatible chat/completions API.

    Returns:
      answer:      the assistant's reply as a string
      diagnostics: a dict with simple metadata, including a crude 'confidence'
    """
    payload = {
        "model": LMSTUDIO_MODEL_ID,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant embedded in an interrogative geometry "
                    "experiment. Answer the user's question clearly and concisely. "
                    "Avoid making claims about having feelings, consciousness, or "
                    "subjective experience. Focus on reasoning and explanation."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        "temperature": 0.7,
        "max_tokens": 512,
        "top_p": 0.95,
    }

    try:
        response = requests.post(LMSTUDIO_BASE_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Expecting OpenAI-style response:
        # { "choices": [ { "message": { "role": "assistant", "content": "..." }, ... } ], ... }
        choices = data.get("choices", [])
        if not choices:
            logger.error("Local LLM returned no choices. Raw response: %s", json.dumps(data)[:500])
            answer = "[LLM ERROR] No choices returned. Echoing question: " + repr(question)
            diagnostics = {
                "engine": "lmstudio",
                "model": LMSTUDIO_MODEL_ID,
                "notes": "No choices returned; fallback echo.",
                "confidence": 0.0,
            }
            return answer, diagnostics

        message = choices[0].get("message", {})
        content = message.get("content", "").strip()

        if not content:
            logger.error("Local LLM returned empty content. Raw response: %s", json.dumps(data)[:500])
            answer = "[LLM ERROR] Empty content. Echoing question: " + repr(question)
            diagnostics = {
                "engine": "lmstudio",
                "model": LMSTUDIO_MODEL_ID,
                "notes": "Empty content; fallback echo.",
                "confidence": 0.0,
            }
            return answer, diagnostics

        # Simple heuristic for "confidence": longer + non-empty answer gets a mid-level confidence.
        # You can replace this later with a more principled measure.
        length = len(content)
        if length < 40:
            confidence = 0.3
        elif length < 200:
            confidence = 0.6
        else:
            confidence = 0.8

        diagnostics = {
            "engine": "lmstudio",
            "model": LMSTUDIO_MODEL_ID,
            "notes": f"LLM answered with {length} characters.",
            "confidence": confidence,
        }
        return content, diagnostics

    except requests.exceptions.RequestException as e:
        logger.error("Error calling local LLM: %s", str(e))
        answer = "[LLM ERROR] Could not reach local LLM. Echoing question: " + repr(question)
        diagnostics = {
            "engine": "lmstudio",
            "model": LMSTUDIO_MODEL_ID,
            "notes": f"RequestException: {e}",
            "confidence": 0.0,
        }
        return answer, diagnostics
    except Exception as e:
        # Catch-all to prevent the whole pipeline from breaking.
        logger.error("Unexpected error in query_local_llm: %s", str(e))
        answer = "[LLM ERROR] Unexpected error. Echoing question: " + repr(question)
        diagnostics = {
            "engine": "lmstudio",
            "model": LMSTUDIO_MODEL_ID,
            "notes": f"Unexpected error: {e}",
            "confidence": 0.0,
        }
        return answer, diagnostics
