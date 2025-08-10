import datetime
from sqlmodel import Field, SQLModel


class CacheMetadata(SQLModel, table=True):
    __tablename__ = "cache_metadata"
    id: int = Field(default=None, primary_key=True)
    last_updated: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Timestamp of the last update to the cache",
    )
