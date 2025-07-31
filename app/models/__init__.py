from sqlalchemy import table
from sqlmodel import SQLModel


class ElwisFtmEntry(SQLModel, table=True):
    __tablename__ = "elwis_ftm_entry"
