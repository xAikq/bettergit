SYSTEM = (
    "You are a senior developer. Generate concise Conventional Commit messages. "
    "Header must be <= 72 chars (no trailing dot). Body is optional. "
    "Respond ONLY with valid JSON (no markdown, no commentary)."
)

USER_TEMPLATE = """\
Heuristics:
- type="{ctype}"
- scope="{scope}"

Stats: +{added}/-{removed}

Changed files:
{files}

Truncated diff:
{diff}

Return JSON in this exact format (NO extra text):
{{
  "type": "feat|fix|docs|refactor|test|chore|build|ci|perf|style",
  "scope": "string or empty",
  "summary": "one line <=72 chars, no period at end",
  "body": "",
  "breaking": false
}}
Only JSON. No commentary.
"""