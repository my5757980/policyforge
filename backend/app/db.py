from sqlmodel import SQLModel, create_engine, Session
from app.models.policy import Policy
from app.models.audit_log import AuditLog
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./policyforge.db")

engine = create_engine(DATABASE_URL, echo=False)


def create_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
