from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str  # BLOCK | ALLOW | LOG
    intent_category: str = ""
    risk_score: float = 0.0
    matched_rule: str = ""
    prompt_excerpt: str = ""
    attack_type: str = ""


class AuditLogResponse(SQLModel):
    id: int
    timestamp: datetime
    action: str
    intent_category: str
    risk_score: float
    matched_rule: str
    prompt_excerpt: str
    attack_type: str
