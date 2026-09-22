"""Database engine, session, and base model setup using SQLAlchemy.

Configured for local SQLite by default, environment-driven via backend.config.
"""

from typing import Generator
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from backend.config import get_settings

settings = get_settings()

# Configure engine with SQLite-specific options when applicable
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for providing a transactional database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create fresh tables and migrate missing columns in existing SQLite databases."""
    Base.metadata.create_all(bind=engine)

    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "tasks" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("tasks")}
    migrations = {
        "answer": "ALTER TABLE tasks ADD COLUMN answer TEXT",
        "verification_status": "ALTER TABLE tasks ADD COLUMN verification_status VARCHAR(64)",
        "evidence_coverage": "ALTER TABLE tasks ADD COLUMN evidence_coverage FLOAT",
        "requires_human_review": "ALTER TABLE tasks ADD COLUMN requires_human_review INTEGER",
        "sources": "ALTER TABLE tasks ADD COLUMN sources TEXT NOT NULL DEFAULT '[]'",
        "findings": "ALTER TABLE tasks ADD COLUMN findings TEXT NOT NULL DEFAULT '[]'",
        "report_id": "ALTER TABLE tasks ADD COLUMN report_id VARCHAR(64)",
    }

    with engine.begin() as connection:
        for column_name, statement in migrations.items():
            if column_name not in existing_columns:
                connection.execute(text(statement))
