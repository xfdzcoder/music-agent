from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator
from urllib.parse import quote_plus

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import config
from core.logger.logger import logger

_engine : Engine | None = None
_SessionLocal : sessionmaker | None = None

def init_db():
    global _engine, _SessionLocal
    # 从环境变量读取配置
    user = config.get_env("POSTGRES_USER")
    password = config.get_env("POSTGRES_PASSWORD")
    host = config.get_env("POSTGRES_HOST")
    port = config.get_env("POSTGRES_PORT")
    db = config.get_env("POSTGRES_DB")

    # 拼接连接字符串
    url = f"postgresql+psycopg://{user}:{quote_plus(password)}@{host}:{port}/{db}"
    _engine = create_engine(url, echo=False, isolation_level="AUTOCOMMIT")
    _SessionLocal = sessionmaker(bind=_engine)
    logger.info("database initialized")

def run_migrations():
    from alembic import command
    from alembic.config import Config

    ini_path = Path(__file__).parent.parent.parent.parent / "alembic.ini"
    toml_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
    alembic_cfg = Config(ini_path, toml_path)
    command.upgrade(alembic_cfg, "head")
    logger.info("database migrated")


def destroy():
    if _engine:
        _engine.dispose()

def get_engine():
    global _engine
    if _engine is None:
        raise Exception("db not initialized")
    return _engine

@contextmanager
def get_session() -> Generator[Session | Any, Any, None]:
    global _engine, _SessionLocal
    if _engine is None or _SessionLocal is None:
        raise Exception("db not initialized")
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error("db exec error: ", e)
        session.rollback()
        raise e
    finally:
        session.close()

