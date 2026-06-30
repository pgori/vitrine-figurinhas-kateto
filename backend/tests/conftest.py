from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlalchemy.engine import Engine

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture()
def database_url(tmp_path: Path) -> str:
    database_path = tmp_path / "test.db"
    return f"sqlite:///{database_path.as_posix()}"


@pytest.fixture()
def engine(database_url: str) -> Generator[Engine, None, None]:
    _run_migrations(database_url)
    test_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False, "timeout": 30},
    )

    try:
        yield test_engine
    finally:
        test_engine.dispose()


@pytest.fixture()
def session(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine, expire_on_commit=False) as test_session:
        yield test_session


@pytest.fixture()
def client(engine: Engine) -> Generator[TestClient, None, None]:
    from app.database import get_session
    from app.main import app

    def override_get_session() -> Generator[Session, None, None]:
        with Session(engine, expire_on_commit=False) as test_session:
            yield test_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def _run_migrations(database_url: str) -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")
