# ACP---II---Project---Experience-Sampling-Method-on-Mobile-Device
ESMisalsoactivelyusedincomputerscience—mostnotablyinthedisciplineofhuman-computer interaction (HCI). Consolvo and Walker (2003) discuss the possibilities of the ESM for ubiquitous computingresearch,specificallytoutingitsabilitytoevaluateatechnological artefact
## First implementation increment

The current skeleton implements the shared study configuration contract and a
FastAPI backend for authenticated study creation, validation, publication, and
immutable versioning. SQLAlchemy supports SQLite for local development and
PostgreSQL for shared environments; Alembic manages schema migrations.

### Local setup

1. Install Python 3.12 or newer.
2. Create an environment with `python3 -m venv .venv`.
3. Install the project with `.venv/bin/pip install -e '.[dev]'`.
4. Apply migrations with `.venv/bin/alembic upgrade head`.
5. Run checks with `.venv/bin/python -m compileall -q backend alembic` and `.venv/bin/pytest -q`.
6. Start the API with `.venv/bin/uvicorn backend.app.main:app --reload`.

The API documentation is available at `http://127.0.0.1:8000/docs` while the
server is running. See `backend/README.md`, `web/README.md`, and
`mobile/README.md` for the current component boundaries.
