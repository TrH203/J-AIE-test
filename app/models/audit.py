from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"

    chat_id = Column(String, primary_key=True)
    question = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    retrieved_docs = Column(ARRAY(String), nullable=False)
    latency_ms = Column(Integer)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    feedback = Column(Text, nullable=True)
