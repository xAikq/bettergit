from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict

__all__ = ["OllamaClient"]


class OllamaClient:
    """Minimal HTTP client for talking to an Ollama instance."""

    def __init__(self, model: str, host: str, temperature: float, max_tokens: int, timeout_s: int = 180) -> None:
        self.model = model
        self.host = host.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_s = timeout_s

    def generate(self, system: str, user: str) -> Dict[str, Any]:
        body = {
            "model": self.model,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        payload = json.dumps(body).encode("utf-8")
        url = f"{self.host}/api/chat"

        for attempt in range(3):
            try:
                request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                    data = json.loads(response.read().decode("utf-8"))
                content = data["message"]["content"].strip()
                return json.loads(_strip_markdown(content))
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                if attempt == 2:
                    raise
                time.sleep(1 + attempt)
        return {}


def _strip_markdown(text: str) -> str:
    if "```" in text:
        text = text.replace("```json", "").replace("```", "")
    return text.strip()
