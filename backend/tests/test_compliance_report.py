"""The compliance report states only what PolicyForge's own data shows: no checklist item is ticked
without evidence, each item says what it was checked against, items PolicyForge cannot see are marked
"not assessed", and the totals count every event.

Run from backend/:  uv run pytest
"""
import os

os.environ.setdefault("GEMINI_API_KEY", "test-key-not-used")  # the Gemini client is built at import; never called here

import pytest
from fastapi import HTTPException
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.audit_log import AuditLog
from app.models.policy import Policy
from app.routers.audit import get_compliance_report

STANDARDS = ["HIPAA", "SOC2", "PCI-DSS"]


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.mark.parametrize("standard", STANDARDS)
def test_nothing_is_ticked_when_there_is_no_evidence(session, standard):
    report = get_compliance_report(standard=standard, session=session)
    ticked = [c["item"] for c in report["checklist"] if c["status"] is True]
    assert ticked == []                     # SOC2 CC6.3 and PCI Req 8.2 used to be ticked unconditionally


@pytest.mark.parametrize("standard, item", [("SOC2", "CC6.3 — Access Removal"),
                                            ("PCI-DSS", "Req 8.2 — User Identity Management")])
def test_what_policyforge_cannot_see_is_marked_not_assessed(session, standard, item):
    session.add(Policy(name="access-control", description="d", yaml_content="rules: []"))
    session.commit()
    row = next(c for c in get_compliance_report(standard=standard, session=session)["checklist"] if c["item"] == item)
    assert row["status"] is None
    assert row["basis"].startswith("Not assessed")


@pytest.mark.parametrize("standard", STANDARDS)
def test_every_item_says_what_it_was_checked_against(session, standard):
    assert all(c["basis"] for c in get_compliance_report(standard=standard, session=session)["checklist"])


def test_evidence_ticks_the_items_it_supports(session):
    session.add(Policy(name="credential-guard", description="d", yaml_content="pii: [ssn]"))
    session.add(AuditLog(action="BLOCK", matched_rule="credential-theft-prevention"))
    session.commit()
    status = {c["item"]: c["status"] for c in get_compliance_report(standard="HIPAA", session=session)["checklist"]}
    assert status["164.312(a)(1) — Access Control"] is True       # policy name mentions credential
    assert status["164.312(b) — Audit Controls"] is True           # there is an audit event
    assert status["164.312(e)(1) — Transmission Security"] is True  # the rules mention SSN
    assert status["164.312(d) — Person Authentication"] is False   # nothing about auth or identity


def test_totals_count_every_event_not_only_the_last_fifty(session):
    session.add_all([AuditLog(action="BLOCK") for _ in range(55)] + [AuditLog(action="ALLOW") for _ in range(5)])
    session.commit()
    report = get_compliance_report(standard="HIPAA", session=session)
    assert report["summary"]["total_events"] == 60                 # was capped at 50
    assert report["summary"]["total_blocked"] == 55
    assert len(report["audit_trail"]) == 20


def test_an_unknown_standard_is_refused_not_shown_as_hipaa(session):
    with pytest.raises(HTTPException) as e:
        get_compliance_report(standard="GDPR", session=session)
    assert e.value.status_code == 400
