# BetterGit Release Notes

## v2.0.1 (2025-09-29)
- Added CLI entrypoint alias so both `bg` and `bgit` run BetterGit.

## v2.0.0 (2025-09-28)
- First public package on PyPI (install via `pip install bettergit`).
- `bg commit` accepts positional messages and keeps `--message/-m` priority.
- Polished terminal feedback for push/suggest flows.

## v1.0.1 (2025-09-28)
- `bg commit` now accepts a positional commit message (`bg commit "..."`).
- The `--message/-m` flag still takes priority over auto-generated messages.
- Polished a few terminal responses for push/suggest flows.
