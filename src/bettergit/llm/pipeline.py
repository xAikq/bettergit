from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict

from bettergit.config import Config
from bettergit.llm.client import OllamaClient
from bettergit.llm.prompts import SYSTEM, USER_TEMPLATE

CommitType = Literal["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore", "build", "ci"]


class LLMCommit(TypedDict, total=False):
    type: CommitType
    scope: str
    summary: str
    body: Optional[str]
    breaking: bool


_TEXT_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".toml",
    ".md",
    ".yml",
    ".yaml",
    ".ini",
    ".txt",
    ".css",
    ".html",
}


def _truncate(text: str, limit: int = 4000) -> str:
    return text if len(text) <= limit else text[:limit] + "\n...[truncated]"


def _filtered_files(files: List[str]) -> List[str]:
    cleaned: List[str] = []
    for path in files:
        lowercase = path.lower()
        if "__pycache__" in lowercase or ".egg-info" in lowercase or lowercase.endswith(".pyc"):
            continue
        if "." in lowercase and lowercase[lowercase.rfind("."):] not in _TEXT_EXTENSIONS:
            continue
        cleaned.append(path)
    return cleaned[:30]


def _client(cfg: Config) -> OllamaClient:
    llm = cfg.llm
    return OllamaClient(
        model=llm.model,
        host=llm.ollama_host,
        temperature=llm.temperature,
        max_tokens=llm.max_tokens,
        timeout_s=llm.http_timeout,
    )


def generate_commit(
    diff: str,
    files: List[str],
    heur_type: str | None,
    heur_scope: str | None,
    added: int,
    removed: int,
    cfg: Config,
) -> LLMCommit:
    user_prompt = USER_TEMPLATE.format(
        ctype=heur_type or "",
        scope=heur_scope or "",
        added=added,
        removed=removed,
        files="\n".join(f"- {path}" for path in _filtered_files(files)),
        diff=_truncate(diff),
    )

    try:
        response: Dict[str, Any] = _client(cfg).generate(SYSTEM, user_prompt)
    except Exception as exc:  # pragma: no cover - fall back to heuristics
        print("LLM ERROR:", exc)
        print("RAW PROMPT:\n", user_prompt)
        return {
            "type": (heur_type or "chore"),
            "scope": (heur_scope or ""),
            "summary": f"auto summary [+{added}/-{removed}]",
            "body": None,
            "breaking": False,
        }

    commit_type = str(response.get("type") or heur_type or "chore").strip()
    scope = str(response.get("scope") or heur_scope or "").strip()
    summary = str(response.get("summary") or f"auto summary [+{added}/-{removed}]").strip()[:72]
    body = response.get("body")
    if not isinstance(body, str) or not body.strip():
        body = None
    breaking = bool(response.get("breaking", False))

    return {
        "type": commit_type,
        "scope": scope,
        "summary": summary,
        "body": body,
        "breaking": breaking,
    }
