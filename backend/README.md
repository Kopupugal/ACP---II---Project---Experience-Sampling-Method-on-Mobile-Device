# Backend skeleton

The backend currently implements the first executable foundation of the ESM platform:

- FastAPI application and health endpoint.
- Strict Pydantic study configuration models.
- User registration and JWT login with Argon2 password hashing.
- Authenticated, owner-isolated study endpoints.
- Draft creation, listing, validation, publication, and new-version endpoints.
- Version history and individual-version retrieval.
- Guarded pause and end lifecycle actions.
- SQLAlchemy persistence for users, studies, and immutable study versions.
- Alembic initial migration for SQLite or PostgreSQL.
- Isolated SQLite tests for authentication and the study lifecycle.

For local development, the default database is `sqlite:///./esm.db`. Set
`ESM_DATABASE_URL` to a PostgreSQL URL for a shared database. Run migrations
with `alembic upgrade head` before starting a production deployment.

Protected study endpoints require a bearer token from `/api/v1/auth/login`.
Published configurations are never edited in place; use
`POST /api/v1/studies/{study_id}/versions` to create a new draft version.
