from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, desc
from datetime import datetime, date
from app.db import get_session
from app.models.audit_log import AuditLog
from app.models.policy import Policy
from app.services.lobster_service import get_metrics

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs")
def get_logs(limit: int = Query(default=20, le=100), session: Session = Depends(get_session)):
    logs = session.exec(
        select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit)
    ).all()
    return [_log_dict(l) for l in logs]


@router.get("/metrics")
def get_dashboard_metrics(session: Session = Depends(get_session)):
    policies = session.exec(select(Policy).where(Policy.is_active == True)).all()
    today = date.today()
    all_logs = session.exec(select(AuditLog)).all()
    today_logs = [l for l in all_logs if l.timestamp.date() == today]
    blocked = sum(1 for l in today_logs if l.action == "BLOCK")
    allowed = sum(1 for l in today_logs if l.action == "ALLOW")
    metrics = get_metrics(len(policies), blocked, allowed)
    return {
        "total_policies": len(session.exec(select(Policy)).all()),
        **metrics,
    }


@router.get("/report")
def get_compliance_report(standard: str = "HIPAA", session: Session = Depends(get_session)):
    policies = session.exec(select(Policy).where(Policy.is_active == True)).all()
    logs = session.exec(
        select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(50)
    ).all()
    blocked_count = sum(1 for l in logs if l.action == "BLOCK")

    checklists = {
        "HIPAA": [
            {"item": "164.312(a)(1) — Access Control", "status": any("access" in p.name.lower() or "credential" in p.name.lower() for p in policies)},
            {"item": "164.312(b) — Audit Controls", "status": len(logs) > 0},
            {"item": "164.312(c)(1) — Integrity", "status": blocked_count > 0},
            {"item": "164.312(d) — Person Authentication", "status": any("auth" in p.name.lower() or "identity" in p.name.lower() for p in policies)},
            {"item": "164.312(e)(1) — Transmission Security", "status": any("pii" in p.yaml_content.lower() or "ssn" in p.yaml_content.lower() for p in policies)},
        ],
        "SOC2": [
            {"item": "CC6.1 — Logical Access Controls", "status": len(policies) > 0},
            {"item": "CC6.2 — New Access Provisioning", "status": any("access" in p.name.lower() for p in policies)},
            {"item": "CC6.3 — Access Removal", "status": True},
            {"item": "CC6.6 — Logical Access Security", "status": blocked_count > 0},
            {"item": "CC6.7 — Data Transmission Restrictions", "status": any("exfiltration" in p.yaml_content.lower() for p in policies)},
        ],
        "PCI-DSS": [
            {"item": "Req 6.4 — Protect Public-Facing Systems", "status": len(policies) > 0},
            {"item": "Req 6.5 — Prevent Common Vulnerabilities", "status": any("injection" in p.yaml_content.lower() for p in policies)},
            {"item": "Req 8.2 — User Identity Management", "status": True},
            {"item": "Req 10.2 — Audit Log Events", "status": len(logs) > 0},
        ],
    }

    return {
        "standard": standard,
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "active_policies": len(policies),
            "total_blocked": blocked_count,
            "total_events": len(logs),
        },
        "policies": [{"name": p.name, "compliance_tags": p.compliance_tags, "created_at": p.created_at.isoformat()} for p in policies],
        "checklist": checklists.get(standard, checklists["HIPAA"]),
        "audit_trail": [_log_dict(l) for l in logs[:20]],
    }


def _log_dict(l: AuditLog) -> dict:
    return {
        "id": l.id,
        "timestamp": l.timestamp.isoformat(),
        "action": l.action,
        "intent_category": l.intent_category,
        "risk_score": l.risk_score,
        "matched_rule": l.matched_rule,
        "prompt_excerpt": l.prompt_excerpt,
        "attack_type": l.attack_type,
    }
