from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
import uuid


class Policy(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: str
    yaml_content: str
    is_active: bool = True
    compliance_tags: str = ""  # comma-separated: "HIPAA,SOC2"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PolicyCreate(SQLModel):
    description: str
    compliance_tags: list[str] = []


class PolicyResponse(SQLModel):
    id: str
    name: str
    description: str
    yaml_content: str
    is_active: bool
    compliance_tags: list[str]
    created_at: datetime
