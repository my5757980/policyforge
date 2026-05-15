from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db import get_session
from app.models.audit_log import AuditLog
from app.services.lobster_service import fire_attack, ATTACK_PROMPTS

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
    attack_type = body.get("attack_type", "prompt_injection")
    result = fire_attack(attack_type)

    log = AuditLog(
        action=result["action"],
        intent_category=result["intent_category"],
        risk_score=result["risk_score"],
        matched_rule=result["matched_rule"],
        prompt_excerpt=ATTACK_PROMPTS.get(attack_type, "")[:100],
        attack_type=attack_type,
    )
    session.add(log)
    session.commit()

    return result
