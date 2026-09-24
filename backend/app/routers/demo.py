from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models.audit_log import AuditLog
from app.models.policy import Policy
from app.services.lobster_service import ATTACK_PROMPTS
from app.services.policy_check import check_prompt

router = APIRouter(prefix="/api/demo", tags=["demo"])

ATTACK_DESCRIPTIONS = {
    "prompt_injection": "Attempt to override system instructions via malicious prompt",
    "pii_exfiltration": "Try to extract SSN, medical records, and PII from the system",
    "credential_theft": "Attempt to steal API keys and environment credentials",
    "jailbreak": "DAN-style jailbreak to bypass all safety restrictions",
    "data_exfiltration": "Try to send customer data to external attacker address",
}


@router.get("/attacks")
def list_attacks():
    return [
        {"type": k, "description": v, "prompt_preview": ATTACK_PROMPTS[k][:80] + "..."}
        for k, v in ATTACK_DESCRIPTIONS.items()
    ]


@router.post("/attack")
def run_attack(body: dict, session: Session = Depends(get_session)):
    """Check one attack prompt against every active policy and record what actually happened."""
    attack_type = body.get("attack_type", "prompt_injection")
    prompt = ATTACK_PROMPTS.get(attack_type)
    if prompt is None:
        raise HTTPException(status_code=400, detail=f"unknown attack type: {attack_type}")

    active = session.exec(
        select(Policy).where(Policy.is_active == True).order_by(Policy.created_at)  # noqa: E712
    ).all()
    result = check_prompt(prompt, [(p.name, p.yaml_content) for p in active])

    log = AuditLog(
        action=result["action"],
        intent_category=result["intent_category"],
        risk_score=result["risk_score"],
        matched_rule=result["matched_rule"],
        prompt_excerpt=prompt[:100],
        attack_type=attack_type,
    )
    session.add(log)
    session.commit()

    return result
