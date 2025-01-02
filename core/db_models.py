from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    String,
    Float,
    UUID,
    DateTime,
    CheckConstraint
)
from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped, 
    mapped_column
)

class Base(DeclarativeBase):
    pass


class Statistics(Base):
    __tablename__ = 'statistics'
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    topic: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(Float)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    __table_args__ = (
        CheckConstraint(value > 0, name='value_min_value')
    ,)
