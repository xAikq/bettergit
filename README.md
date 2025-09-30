# BetterGit (`bg`)

BetterGit is a lightweight command-line companion for Git. It streamlines daily version-control tasks, adds short and memorable commands, and can draft Conventional Commit messages with the help of an LLM.

## Highlights

- Message generation via `bg suggest` (interactive) and `bg commit` (one-shot).
- Staging shortcuts: `bg add` for everything or selected paths.
- Branch utilities: `bg branches`, `bg branch-info`, `bg switch`, `bg create-branch`, `bg delete-branch`.
- Tag utilities: `bg tag` to review tags, `bg create-tag` to add new ones, `bg delete-tag` to clean up.
- Simple pushes: `bg push` for the current branch, `bg push-to` for any branch without switching.
- Interactive branch deletion that asks whether to drop the remote copy as well.
- Rich top-level help (`bg --help`) that doubles as a quick reference.

## Quick install

```bash
pip install --upgrade bettergit
bg --help
```

> Prefer editable mode for development? See the "Source installation" section inside the guide below.

## User guide

A full walkthrough of commands, options, and workflows lives in [docs/USER_GUIDE.md](docs/USER_GUIDE.md).

## License

Released under the [MIT](LICENSE) license.
