from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, desc, func
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


# PolicyForge sees only its own policies and audit log, so each checklist item says exactly what it was
# checked against (evidence, not certification). What that data cannot show is "not assessed" (None).
NOT_ASSESSED_USERS = "Not assessed: PolicyForge has no user accounts to provision, remove or identify."


def _item(item: str, status: bool | None, basis: str) -> dict:
    return {"item": item, "status": status, "basis": basis}


@router.get("/report")
def get_compliance_report(standard: str = "HIPAA", session: Session = Depends(get_session)):
    policies = session.exec(select(Policy).where(Policy.is_active == True)).all()
    total_events = session.exec(select(func.count()).select_from(AuditLog)).one()
    blocked_count = session.exec(select(func.count()).select_from(AuditLog).where(AuditLog.action == "BLOCK")).one()
    recent = session.exec(
        select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(20)
    ).all()

    def named(*words: str) -> bool:
        return any(w in p.name.lower() for p in policies for w in words)

    def mentions(*words: str) -> bool:
        return any(w in p.yaml_content.lower() for p in policies for w in words)

    checklists = {
        "HIPAA": [
            _item("164.312(a)(1) — Access Control", named("access", "credential"),
                  "An active policy's name mentions access or credential."),
            _item("164.312(b) — Audit Controls", total_events > 0, "The audit log holds at least one event."),
            _item("164.312(c)(1) — Integrity", blocked_count > 0, "At least one attack was blocked."),
            _item("164.312(d) — Person Authentication", named("auth", "identity"),
                  "An active policy's name mentions auth or identity."),
            _item("164.312(e)(1) — Transmission Security", mentions("pii", "ssn"),
                  "An active policy's rules mention PII or SSN."),
        ],
        "SOC2": [
            _item("CC6.1 — Logical Access Controls", len(policies) > 0, "At least one policy is active."),
            _item("CC6.2 — New Access Provisioning", named("access"), "An active policy's name mentions access."),
            _item("CC6.3 — Access Removal", None, NOT_ASSESSED_USERS),
            _item("CC6.6 — Logical Access Security", blocked_count > 0, "At least one attack was blocked."),
            _item("CC6.7 — Data Transmission Restrictions", mentions("exfiltration"),
                  "An active policy's rules mention exfiltration."),
        ],
        "PCI-DSS": [
            _item("Req 6.4 — Protect Public-Facing Systems", len(policies) > 0, "At least one policy is active."),
            _item("Req 6.5 — Prevent Common Vulnerabilities", mentions("injection"),
                  "An active policy's rules mention injection."),
            _item("Req 8.2 — User Identity Management", None, NOT_ASSESSED_USERS),
            _item("Req 10.2 — Audit Log Events", total_events > 0, "The audit log holds at least one event."),
        ],
    }
    if standard not in checklists:
        raise HTTPException(400, f"Unknown standard {standard!r}. Choose one of: {', '.join(checklists)}.")

    return {
        "standard": standard,
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "active_policies": len(policies),
            "total_blocked": blocked_count,
            "total_events": total_events,
        },
        "policies": [{"name": p.name, "compliance_tags": p.compliance_tags, "created_at": p.created_at.isoformat()} for p in policies],
        "checklist": checklists[standard],
        "audit_trail": [_log_dict(l) for l in recent],
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
