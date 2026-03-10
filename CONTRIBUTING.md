# Contributing Guide

First off: thanks for investing time in this project. Contributions are welcome and appreciated, whether you’re fixing edge cases, improving ranking logic, hardening data flows, or polishing docs.

This repo is a practical research tool, so contributions should optimize for reliability, reproducibility, and signal quality.

## I Have a Question

Please **do not** use GitHub Issues for general usage questions.

Issues are reserved for actionable engineering work (bugs, enhancements, regressions). For questions, use one of these channels instead:

- GitHub Discussions (preferred, if enabled)
- Stack Overflow (`streamlit`, `python`, `google-play-scraper` tags)
- Maintainer social links in `README.md`

When asking a question, include:

- What you’re trying to achieve
- What you already tried
- Relevant logs/screenshots
- Your runtime environment

## Reporting Bugs

Before opening a bug report:

1. Check existing open/closed issues for duplicates.
2. Re-test on the latest `main` branch.
3. Verify the issue is reproducible with clean local state if possible (e.g., clear `seen_apps.db`).

### Bug report checklist

A high-quality report includes:

- **Environment**
  - OS and version
  - Python version
  - `streamlit` version
  - project commit SHA/branch
- **Steps to reproduce**
  - deterministic sequence from launch to failure
- **Expected behavior**
  - what should happen
- **Actual behavior**
  - what happened instead
- **Artifacts**
  - logs, stack traces, screenshots, sample CSV output (if relevant)

## Suggesting Enhancements

Enhancement proposals are welcome, but keep them problem-first.

Good feature requests include:

- **Problem statement:** what pain point exists today
- **Proposed change:** what you want to add/modify
- **Use cases:** concrete scenarios and target users
- **Tradeoffs:** complexity, performance, or maintenance cost

If your proposal alters ranking/scoring behavior, include before/after examples.

## Local Development / Setup

```bash
# 1) Fork on GitHub, then clone your fork
git clone https://github.com/<your-username>/App-Finder-100k.git
cd App-Finder-100k

# 2) Create virtual env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4) Run app locally
streamlit run app.py
```

No `.env` bootstrap is required right now. Runtime settings are managed in `config.py`.

## Pull Request Process

### Branch strategy

Use descriptive branch names:

- `feature/<short-slug>`
- `bugfix/<issue-id-or-slug>`
- `docs/<short-slug>`
- `refactor/<short-slug>`

Examples:

- `feature/locale-weighting`
- `bugfix/123-install-parse`
- `docs/readme-refresh`

### Commit style

Use **Conventional Commits**:

- `feat: add locale prioritization toggle`
- `fix: handle missing install strings in parser`
- `docs: rewrite README and add contribution guide`
- `refactor: split UI rendering helpers`
- `test: add novelty score unit coverage`

### Sync with upstream

Before opening PR, sync with latest `main`:

```bash
git fetch upstream
git rebase upstream/main
```

### PR description requirements

Every PR should include:

- Summary of changes
- Why the change is needed
- Testing notes (commands + outcomes)
- Linked issue(s) (`Closes #123` when applicable)
- Screenshots/GIFs for UI-visible changes

Keep PRs focused. A small, surgical PR merges faster than a giant mixed bag.

## Styleguides

### Code quality

- Follow existing project structure and naming.
- Prefer readable, explicit logic over “clever” one-liners.
- Keep functions single-purpose and composable.
- Avoid unrelated refactors in functional PRs.

### Tooling

This repo currently has minimal enforced tooling.

Recommended local checks:

```bash
python -m compileall .
```

If you introduce new tooling (formatter/linter/test framework), include config in the same PR and document why it improves team velocity.

### Architecture conventions

- `app.py`: orchestration layer only.
- `ui.py`: Streamlit widgets/rendering concerns.
- `scraper.py`: external data collection and filtering logic.
- `db.py`: persistence/cache primitives.
- `scoring.py`: ranking and novelty logic.
- `config.py`: constants/defaults.

## Testing

All new behavior should be validated before PR submission.

Minimum expectation:

- Run syntax sanity checks.
- Run the app and exercise affected path manually.
- Validate no regression in CSV export and sidebar controls when relevant.

Suggested commands:

```bash
python -m compileall .
streamlit run app.py
```

If you add non-trivial logic (especially scoring or parsing), include automated tests.

## Code Review Process

- Maintainer reviews incoming PRs.
- Expect at least one approval before merge.
- Address review comments with incremental commits or clean fixup/squash.
- If feedback is unclear, ask for clarification in the PR thread.

Review SLA can vary. If a PR is stale, rebase on latest `main`, resolve conflicts, and post a short status update.

Thanks for helping make App Finder 100k more robust and useful.
