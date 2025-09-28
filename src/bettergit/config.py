from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

__all__ = ["LLMConfig", "Config", "load_config"]


@dataclass
class LLMConfig:
    enabled: bool = True
    provider: str = "ollama"
    model: str = "phi3.5:3.8b"
    temperature: float = 0.1
    max_tokens: int = 256
    ollama_host: str = "http://localhost:11434"
    http_timeout: int = 180


@dataclass
class Config:
    scope_mode: str = "first_dir"
    llm: LLMConfig = field(default_factory=LLMConfig)


def load_config(path: Optional[str] = None) -> Config:
    """Load configuration from *path*.

    Currently returns default values until file-based configuration is implemented.
    """

    return Config()
