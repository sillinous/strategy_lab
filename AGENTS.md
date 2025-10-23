# Repository Guidelines

This guide helps contributors work effectively in this repo.

## Project Structure & Module Organization
- Root layout: `backend/` (FastAPI service, primary code) and `frontend/` (Next.js scaffold in `frontend/nextjs_space/`).
- Backend source: `backend/app/` with submodules `api/`, `core/`, `models/`, `schemas/`, `services/`, `utils/`.
- Tests: `backend/tests/` and a quick check in `backend/test_quick.py`.
- Runtime assets: `backend/data/` (cache) and `backend/logs/` (created at runtime).

## Build, Test, and Development Commands
- Create venv: `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`).
- Install deps: `pip install -r backend/requirements.txt`.
- Run dev API: `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` from `backend/`.
- Alt run: `python -m app.main` from `backend/`.
- Tests: `pytest` (from `backend/`).
- Coverage: `pytest --cov=app --cov-report=html` (report in `backend/htmlcov/`).

## Coding Style & Naming Conventions
- Python 3.11+, 4‑space indentation, Black/PEP8 style; prefer explicit imports.
- Files: snake_case (`data_fetcher.py`), classes: `PascalCase`, functions/vars: `snake_case`.
- API routers grouped by domain in `backend/app/api/*.py`; schemas mirror models in `schemas/`.
- Keep modules small and unit-testable; avoid circular imports by using service boundaries.

## Testing Guidelines
- Framework: `pytest` (+ `pytest-asyncio` when needed).
- Place tests under `backend/tests/` mirroring package paths, e.g., `tests/services/test_backtester.py`.
- Name tests `test_*.py`; aim for coverage on services, indicators, and API routes via `fastapi.testclient`.
- Use fixtures to isolate DB and filesystem; do not write outside temp dirs.

## Commit & Pull Request Guidelines
- Commits: imperative, concise subject (<=72 chars). Example: `feat(api): add backtest metrics endpoint`.
- Include focused diffs; reference issues with `Closes #123` when applicable.
- PRs: clear description, scope, manual test notes, and screenshots for API responses when relevant (e.g., `/docs`).
- CI expectations: lint passes locally, tests green, no secrets committed (use `.env.example`).

## Security & Configuration Tips
- Copy `backend/.env.example` to `.env`; never commit real credentials or tokens.
- Default DB is SQLite; ensure test runs use isolated DB paths.
- CORS and logging configured in `app/main.py`; adjust via settings in `app/core/config.py`.

## Architecture Overview
- FastAPI app entrypoint: `backend/app/main.py` with routers in `app/api/` and business logic in `app/services/`.
- Persistence via SQLAlchemy models in `app/models/`; request/response validation via Pydantic `app/schemas/`.

