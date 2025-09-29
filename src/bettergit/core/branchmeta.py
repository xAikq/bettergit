from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from bettergit.core import gitio

_METADATA_SUBDIR = 'bettergit'
_METADATA_FILENAME = 'branch_origins.json'


def _git_dir() -> Path:
    raw = gitio._run_git(['rev-parse', '--git-dir'])  # type: ignore[attr-defined]
    path = Path(raw)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def _metadata_path() -> Path:
    return _git_dir() / _METADATA_SUBDIR / _METADATA_FILENAME


def _load_origins() -> Dict[str, str]:
    path = _metadata_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}


def _write_origins(data: Dict[str, str]) -> None:
    path = _metadata_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding='utf-8')


def record_origin(branch: str, start_point: str | None) -> None:
    data = _load_origins()
    if start_point:
        data[branch] = start_point
    else:
        data.pop(branch, None)
    _write_origins(data)


def get_origin(branch: str) -> str | None:
    return _load_origins().get(branch)


def load_all() -> Dict[str, str]:
    return _load_origins()
