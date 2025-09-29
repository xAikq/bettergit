# BetterGit User Guide

BetterGit (`bg`) is a productivity layer on top of Git. It keeps everyday tasks short, provides guard rails for branches, and can craft Conventional Commit messages with an LLM when you want help.

## Table of contents
- [Requirements](#requirements)
- [Installation](#installation)
  - [Install from GitHub with pip](#install-from-github-with-pip)
  - [Install from source](#install-from-source)
  - [Install and run Ollama](#install-and-run-ollama)
- [Quick start](#quick-start)
- [Command cheat sheet](#command-cheat-sheet)
- [Command reference](#command-reference)
  - [`bg add`](#bg-add)
  - [`bg suggest`](#bg-suggest)
  - [`bg commit`](#bg-commit)
  - [`bg branches`](#bg-branches)
  - [`bg branch-info`](#bg-branch-info)
  - [`bg switch`](#bg-switch)
  - [`bg create-branch`](#bg-create-branch)
  - [`bg delete-branch`](#bg-delete-branch)
  - [`bg push`](#bg-push)
  - [`bg push-to`](#bg-push-to)
- [Typical workflows](#typical-workflows)
  - [Commit from start to finish](#commit-from-start-to-finish)
  - [Branch lifecycle](#branch-lifecycle)
- [AI assistance for commit messages](#ai-assistance-for-commit-messages)
- [Configuration](#configuration)
- [Updating BetterGit](#updating-bettergit)
- [Troubleshooting](#troubleshooting)

## Requirements
- Python 3.10 or newer
- Git available on your PATH
- Optional for AI features: an HTTP-accessible LLM provider (defaults to a local Ollama service at `http://localhost:11434`)

## Installation

### Install from GitHub with pip

```bash
pip install --upgrade bettergit
```

This pulls the latest commit from the `main` branch. Swap `main` for another branch or tag if needed.

### Install from source

```bash
git clone https://github.com/xAikq/bettergit.git
cd bettergit
python -m venv venv
venv\Scripts\activate      # Windows
# or
source venv/bin/activate    # Linux / macOS

pip install -e .
```

The editable install keeps the `bg` entry point in sync with the code inside `src/`.

### Install and run Ollama

BetterGit can ask an LLM to draft commit messages. By default we talk to [Ollama](https://ollama.com) running on your localhost.

1. **Download Ollama**
   - **macOS**: `brew install ollama` or grab the `.pkg` installer from the website.
   - **Linux**: follow the [official instructions](https://ollama.com/download) (`curl -fsSL https://ollama.com/install.sh | sh`).
   - **Windows**: install the MSI preview from the same download page (requires Windows 10/11 x64). Running through WSL also works if the host supports it.

2. **Start the daemon**
   ```bash
   ollama serve
   ```
   On macOS/Windows the desktop app usually keeps the server running automatically.

3. **Pull the model we use by default**
   ```bash
   ollama pull phi3.5:3.8b
   ```
   (Feel free to experiment with other models—adjust `bettergit.config.Config.llm.model` or use CLI overrides.)

4. **Smoke-test** that the API is reachable:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   If the server is responding, BetterGit will reach it too.

> **Tip:** keep Ollama running in the background. If it is not available, `bg suggest`/`bg commit` fall back to heuristics; you can also disable LLM usage explicitly with `--no-llm`.

## Quick start
1. Stage your changes with `bg add` (all files) or `bg add path/to/file.py` (selection).
2. Run `bg suggest`, review or edit the proposed message, confirm with `c` to commit.
3. Publish the branch with `bg push`. On the first run the command adds `-u origin <branch>` automatically.
4. Clean up merged branches with `bg delete-branch feature/foo --remote-delete` to remove both local and remote copies.

## Command cheat sheet

| Command            | What it does                                             | Core options |
|--------------------|----------------------------------------------------------|--------------|
| `bg add`           | Stage everything or specific paths                       | `--config/-c` |
| `bg suggest`       | Interactive Conventional Commit recommendation           | `--llm/--no-llm`, `--config/-c` |
| `bg commit`        | One-shot commit using the generated message              | `--llm/--no-llm`, `--config/-c` |
| `bg branches`      | List branches (add remotes with `--all/-a`)              | `--all/-a`, `--config/-c` |
| `bg branch-info`   | Show tracking target, ahead/behind, last commit summary  | `--branch/-b`, `--config/-c` |
| `bg switch`        | Check out another branch                                 | `--config/-c` |
| `bg create-branch` | Create a branch, optionally switch/overwrite             | `--from/-f`, `--no-switch`, `--force/-F`, `--config/-c` |
| `bg delete-branch` | Delete a local branch and optionally the remote copy     | `--remote/-r`, `--remote-delete`, `--no-prompt`, `--force/-F`, `--config/-c` |
| `bg push`          | Push the current or selected branch                      | `--branch/-b`, `--remote/-r`, `--no-set-upstream`, `--config/-c` |
| `bg push-to`       | Push any branch without switching                        | `--remote/-r`, `--no-set-upstream`, `--config/-c` |

## Command reference

### `bg add`
Stages changes. Without arguments it mirrors `git add -A`. With paths it acts like `git add -- <paths...>`.

### `bg suggest`
Analyses staged changes, proposes a Conventional Commit summary, displays it inside a box, and waits for an action:
- `c` / `commit` - accept and commit
- `e` / `edit` - open the message in your editor (uses `$EDITOR` if set)
- `r` / `regen` - generate again from the diff
- `q` / `quit` - abort without committing
The `--llm` / `--no-llm` toggles override the default model usage for the current run.

### `bg commit`
Skips the interactive step and commits immediately after the message is generated. Ideal for automation or when you already trust the suggestion.

### `bg branches`
Groups branches by category, marking the current one with `*` and highlighting local standalone branches, remote branches, remote HEAD pointers, and branches created via `bg create-branch --from`; derived branches also show their parent. Include `--all/-a` to show remote branches.

### `bg branch-info`
Reports the upstream reference, ahead/behind counts, and the last commit (SHA, author, date, title). Use `--branch/-b` to inspect a non-current branch.

### `bg switch`
Light wrapper around `git checkout <branch>`.

### `bg create-branch`
Creates a branch and, by default, switches to it.
- `--from/-f REF` - specify the starting point (commit, tag, or branch)
- `--no-switch` - create but stay on the current branch
- `--force/-F` - reuse the branch name (`git switch -C` or `git branch -f`)

### `bg delete-branch`
Deletes the local branch with `git branch -d` or `-D` (when `--force` is set). After success it asks whether to delete the remote branch as well. Automation flags:
- `--remote-delete` - delete the remote copy without prompting
- `--no-prompt` - skip the question and keep the remote branch
- `--remote/-r` - choose a remote other than `origin`

### `bg push`
Pushes the current branch (or one supplied via `--branch/-b`). When the branch does not have an upstream yet, BetterGit sends `git push -u <remote> <branch>` unless you provide `--no-set-upstream`.

### `bg push-to`
Pushes any branch without switching to it first. Useful for publishing fix branches while staying on `main`.

## Typical workflows

### Commit from start to finish
```bash
bg add src/service.py
bg suggest          # review, edit, or accept the message
bg push             # pushes current branch; first push sets upstream
```

### Branch lifecycle
```bash
bg create-branch feature/payments --from main
# ... make changes and commit ...
bg push
# ... merge the branch / open a PR ...
bg delete-branch feature/payments --remote-delete
```
`bg delete-branch` first removes the local branch, then runs `git push origin --delete feature/payments` (or another remote if you used `--remote`).

## AI assistance for commit messages
- LLM support is enabled by default. The default provider is `ollama` with model `phi3.5:3.8b`, temperature `0.1`, max tokens `256`.
- If the provider is unavailable, commands fall back to Git errors. You can disable the model for a run with `--no-llm` or force it with `--llm`.
- To swap models or providers, update `bettergit.config.Config.llm` (or pass overrides through `--config/-c`).
- Want to run headless? Keep `ollama serve` running as a systemd service/Windows task and expose it on `http://localhost:11434`.

## Configuration
`bettergit.config.Config` currently returns static values. Commands accept `--config/-c` so future releases can load a `bg.toml` (or similar). Until then, use the CLI flags to toggle behaviour.

## Updating BetterGit

```bash
pip install --upgrade bettergit
```

For an editable install, pull the latest changes (`git pull`) and reinstall if needed (`pip install -e . --upgrade`).

## Troubleshooting
- **"bg" not found** - make sure the right virtual environment is active or reinstall the package.
- **AI request fails** - verify that your Ollama (or another provider) instance accepts requests at the configured URL, or add `--no-llm`.
- **Remote branch still exists** - rerun `bg delete-branch feature/foo --remote-delete` or manually push `git push origin --delete feature/foo`.
- **Prefer raw Git output** - you can always drop back to Git directly; BetterGit surfaces Git error messages without masking them.
