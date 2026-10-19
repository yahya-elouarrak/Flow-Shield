from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

class TimestampMixin(SQLModel):
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
