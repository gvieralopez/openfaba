# Developers

This document contains developer-focused setup, testing, and build instructions
for working on and contributing to openFABA from source.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — python project manager
- [make](https://www.gnu.org/software/make/) (optional) — used for convenience commands in the `Makefile`

## Installation (from source)

Install dependencies into the local virtual environment:

```bash
uv sync --all-groups
```

Activate the virtual environment:

On Linux / macOS:

```bash
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
# If PowerShell policy prevents running the script:
powershell -ExecutionPolicy Bypass -File .venv\Scripts\Activate.ps1
```

On Windows (CMD):

```cmd
.venv\Scripts\activate.bat
```

## Common development tasks

All convenience commands are available in the `Makefile`.

### Linting, formatting, and type checking

```bash
make qa
```

Runs `ruff` for linting/formatting and `mypy` for type checks.

### Run tests

Before running tests, review `.env.test` and set any required environment variables.

```bash
make test
```

Runs the test suite using `pytest`.

### Build distribution

```bash
make build
```

Creates a distribution package in `dist/`.

### Clean

```bash
make clean
```

Removes build artifacts and caches.

### Bumping version

```bash
make version
```

Interactive version bump helper.

## Notes

- Keep README.md focused on non-developer usage; move developer instructions here.
- When editing repository setup, update this file accordingly.


---

<sub>🚀 Project starter provided by [Cookie Pyrate](https://github.com/gvieralopez/cookie-pyrate)</sub>