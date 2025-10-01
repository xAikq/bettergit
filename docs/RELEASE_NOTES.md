# BetterGit Release Notes

## v2.1.2 (2025-10-02)
- `bg branches` is now `bg branch`.
- Fixed misspelling of `create-tag` in `bettergit.core.gitio`.

## v2.1.1 (2025-10-02)
- `bg create-tag` now asks whether to push the new tag to the selected remote (defaults to `origin`).
- `bg delete-tag` detects matching remote tags, offers to delete them, and respects `--remote/-r`.
- Added `bg delete-remote-tag` for direct remote tag cleanup plus supporting helpers in `bettergit.core.gitio`.

## v2.1.0 (2025-10-01)
- Added tag management commands (`bg tag`, `bg create-tag`, `bg delete-tag`) to streamline release workflows.
- `bg create-tag` now accepts an optional positional message to create annotated tags without extra flags.

## v2.0.2 (2025-09-29)
- `bg branches` now shows all available branches (highlighting is also implemented).

## v2.0.1 (2025-09-29)
- Added CLI entrypoint alias so both `bg` and `bgit` run BetterGit.

## v2.0.0 (2025-09-28)
- First public package on PyPI (install via `pip install bettergit`).

## v1.0.1 (2025-09-28)
- `bg commit` now accepts a positional commit message (`bg commit "..."`).
- The `--message/-m` flag still takes priority over auto-generated messages.
- Polished a few terminal responses for push/suggest flows.
