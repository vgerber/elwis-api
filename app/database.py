import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

DB_TYPE = os.getenv("DB_TYPE", "postgres")

if DB_TYPE == "sqlite":
    SQLITE_PATH = os.getenv("SQLITE_PATH", "sqlite.db")
    db_url = f"sqlite:///{SQLITE_PATH}"
    connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, echo=False, connect_args=connect_args)
elif DB_TYPE == "postgres":
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(db_url, echo=False)
else:
    raise ValueError(
        f"Unsupported DB_TYPE: {DB_TYPE}. Supported types are 'sqlite' and 'postgres'."
    )


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine, autoflush=True) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
