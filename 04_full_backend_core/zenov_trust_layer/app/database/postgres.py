from contextlib import contextmanager
from typing import Iterator, Optional

from ..config import settings

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session, sessionmaker
except ImportError:  # pragma: no cover - dependency optional in local doc-only mode
    create_engine = None
    text = None
    Session = object
    sessionmaker = None


_engine = None
_SessionLocal = None


def is_postgres_configured() -> bool:
    return bool(settings.database_url and create_engine and sessionmaker)


def get_engine():
    global _engine
    if not is_postgres_configured():
        return None
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine


def get_session_factory():
    global _SessionLocal
    engine = get_engine()
    if engine is None:
        return None
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return _SessionLocal


@contextmanager
def session_scope() -> Iterator[Optional[Session]]:
    factory = get_session_factory()
    if factory is None:
        yield None
        return
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def postgres_status() -> dict:
    if not is_postgres_configured():
        return {"configured": False, "connected": False, "mode": "memory_fallback"}
    try:
        with session_scope() as session:
            session.execute(text("SELECT 1"))
        return {"configured": True, "connected": True, "mode": "postgres"}
    except Exception as exc:
        return {"configured": True, "connected": False, "mode": "memory_fallback", "error": str(exc)}
