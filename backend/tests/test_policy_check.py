"""Attacks are checked against the active policies for real: the outcome follows the rules the policies
actually contain, and nothing (no risk score, no intent) is invented.

Uses the app's own demo policies and attack prompts. Run from backend/:  uv run pytest
"""
import os

os.environ.setdefault("GEMINI_API_KEY", "test-key-not-used")  # the Gemini client is built at import; never called here

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.services.gemini_service import _DEMO_POLICIES
from app.services.lobster_service import ATTACK_PROMPTS
from app.services.policy_check import check_prompt

CREDENTIAL = ("credential", _DEMO_POLICIES["credential"])
HIPAA = ("hipaa", _DEMO_POLICIES["hipaa"])
INJECTION = ("injection", _DEMO_POLICIES["injection"])


def test_credential_theft_is_blocked_by_the_credential_policy():
    r = check_prompt(ATTACK_PROMPTS["credential_theft"], [CREDENTIAL])
    assert (r["action"], r["matched_rule"]) == ("BLOCK", "credential-theft-prevention")
    assert "keyword 'password'" in r["matched_on"]
    assert any(e.startswith("pii api_key") for e in r["matched_on"])


def test_a_policy_that_does_not_cover_jailbreaks_lets_one_through():
    r = check_prompt(ATTACK_PROMPTS["jailbreak"], [CREDENTIAL])
    assert (r["action"], r["matched_rule"]) == ("ALLOW", "none")


def test_rules_are_really_evaluated_not_assumed():
    # "ignore previous" does not match "Ignore ALL previous", so the first rule misses and the second one catches it
    r = check_prompt(ATTACK_PROMPTS["prompt_injection"], [INJECTION])
    assert (r["action"], r["matched_rule"]) == ("BLOCK", "instruction-override-guard")
    assert "keyword 'you are now'" in r["matched_on"]


def test_a_pii_request_is_blocked_by_the_hipaa_policy():
    r = check_prompt(ATTACK_PROMPTS["pii_exfiltration"], [HIPAA])
    assert (r["action"], r["matched_rule"]) == ("BLOCK", "hipaa-phi-protection")
    assert "keyword 'patient'" in r["matched_on"]
    assert any(e.startswith("pii ssn") for e in r["matched_on"])


def test_with_no_active_policy_nothing_is_blocked():
    r = check_prompt(ATTACK_PROMPTS["prompt_injection"], [])
    assert (r["action"], r["message"]) == ("ALLOW", "No active policy to check against.")


def test_no_score_is_invented_and_the_result_says_what_was_not_checked():
    r = check_prompt(ATTACK_PROMPTS["credential_theft"], [CREDENTIAL])
    assert r["risk_score"] is None and r["intent_category"] == "not_checked"
    assert (r["engine"], r["not_checked"]) == ("policyforge-local", ["intent"])


def test_keywords_match_whole_words_only():
    policy = ("p", "rules:\n  - name: r\n    match:\n      keywords: [pass]\n    action: DENY\n")
    assert check_prompt("please read this passage aloud", [policy])["action"] == "ALLOW"
    assert check_prompt("give me the pass", [policy])["action"] == "BLOCK"


def test_intent_only_rules_and_broken_policies_are_reported_not_hidden():
    intent_only = ("i", "rules:\n  - name: intent-only\n    match:\n      intent: [jailbreak]\n    action: DENY\n")
    broken = ("b", "rules: [unclosed")
    r = check_prompt(ATTACK_PROMPTS["jailbreak"], [intent_only, broken])
    assert r["action"] == "ALLOW"
    assert (r["unchecked_rules"], r["skipped_policies"]) == (["intent-only"], ["b"])


def test_a_log_rule_logs_instead_of_blocking():
    policy = ("l", "rules:\n  - name: watch-dan\n    match:\n      keywords: [dan]\n    action: LOG\n")
    assert check_prompt(ATTACK_PROMPTS["jailbreak"], [policy])["action"] == "LOG"


# ── the API route ──────────────────────────────────────────────────────────
@pytest.fixture
def api():
    from app.db import get_session
    from app.main import app
    from app.models.policy import Policy

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(Policy(name="credential", description="d", yaml_content=_DEMO_POLICIES["credential"], is_active=True))
        s.add(Policy(name="retired-dan-block", description="d", is_active=False,
                     yaml_content="rules:\n  - name: dan\n    match:\n      keywords: [dan]\n    action: DENY\n"))
        s.commit()

    def session():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = session
    yield TestClient(app), engine
    app.dependency_overrides.clear()


def test_the_attack_route_checks_only_active_policies_and_logs_the_real_decision(api):
    client, engine = api
    blocked = client.post("/api/demo/attack", json={"attack_type": "credential_theft"}).json()
    allowed = client.post("/api/demo/attack", json={"attack_type": "jailbreak"}).json()  # only an inactive policy would block it
    assert (blocked["action"], blocked["matched_rule"]) == ("BLOCK", "credential-theft-prevention")
    assert allowed["action"] == "ALLOW"

    from app.models.audit_log import AuditLog
    with Session(engine) as s:
        logs = s.exec(select(AuditLog).order_by(AuditLog.id)).all()
    assert [(l.action, l.matched_rule, l.risk_score) for l in logs] == [
        ("BLOCK", "credential-theft-prevention", None),
        ("ALLOW", "none", None),
    ]


def test_an_unknown_attack_type_is_an_error_not_a_result(api):
    client, _ = api
    assert client.post("/api/demo/attack", json={"attack_type": "made_up"}).status_code == 400
