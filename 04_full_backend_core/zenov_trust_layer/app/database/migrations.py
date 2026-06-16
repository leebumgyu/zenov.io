from __future__ import annotations

from pathlib import Path

from .postgres import is_postgres_configured, session_scope, text


SCHEMA_FILES = [
    "016_partner_hub_schema.sql",
    "031_partner_pipeline_production_schema.sql",
]


def initialize_postgres_schema() -> dict:
    """Apply the minimal partner pipeline schema when PostgreSQL is configured."""
    if not is_postgres_configured():
        return {"configured": False, "applied": False, "schemas": []}

    schema_dir = Path(__file__).resolve().parents[3] / "db" / "postgres"
    applied: list[str] = []
    with session_scope() as session:
        for filename in SCHEMA_FILES:
            sql_path = schema_dir / filename
            sql = sql_path.read_text(encoding="utf-8")
            for statement in [part.strip() for part in sql.split(";") if part.strip()]:
                session.execute(text(statement))
            applied.append(filename)
    return {"configured": True, "applied": True, "schemas": applied}
