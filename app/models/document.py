from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import VECTOR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(VECTOR(768))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
