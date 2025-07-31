from sqlmodel import SQLModel


def create_db_and_tables():
    SQLModel.metadata.create_all(bind=SQLModel.engine)
