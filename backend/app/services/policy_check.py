"""Check a prompt against the active PolicyForge policies, for real.

Each rule's `keywords` and `pii` lists are evaluated against the prompt: a rule matches when any listed
keyword appears in it as a whole word or phrase (case-insensitive), or any listed PII type is named or
present in it. Rules are tried policy by policy, top to bottom, and the first match decides. A rule's
`intent` list is not evaluated: telling intent apart needs a classifier, so results say so instead of
guessing, and no risk score is invented.
"""
import re
import time

import yaml

ENGINE = "policyforge-local"
CHECKED = ["keywords", "pii"]
NOT_CHECKED = ["intent"]
ACTIONS = {"DENY": "BLOCK", "ALLOW": "ALLOW", "LOG": "LOG"}

# A PII type counts as present when the prompt names it, or contains a value that looks like it.
_PII_WORDS = {
    "ssn": ["ssn", "social security number", "social security"],
    "credit_card": ["credit card", "card number"],
    "api_key": ["api key", "api keys", "access key", "secret key"],
    "password": ["password", "passwords", "passwd"],
    "medical_record": ["medical record", "medical records", "mrn", "health record"],
    "email": ["email", "emails", "e mail"],
}
_PII_VALUES = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "api_key": re.compile(r"\b(?:sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16})\b"),
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
}


def _words(text: str) -> str:
    """Lower-cased, every run of other characters (underscores too) made one space, padded with spaces."""
    return " " + re.sub(r"[^0-9a-z]+", " ", str(text).lower()).strip() + " "


def _has_phrase(words: str, phrase: str) -> bool:
    p = _words(phrase)
    return p.strip() != "" and p in words


def _pii_evidence(prompt: str, words: str, kind: str) -> str | None:
    for w in _PII_WORDS.get(str(kind).lower(), []):
        if _has_phrase(words, w):
            return w
    value = _PII_VALUES.get(str(kind).lower())
    found = value.search(prompt) if value else None
    return found.group(0) if found else None


def check_prompt(prompt: str, policies: list[tuple[str, str]]) -> dict:
    """Decide what the active policies do with `prompt`. `policies` holds (name, YAML) of every active one."""
    started = time.perf_counter()
    words = _words(prompt)
    unchecked_rules, skipped_policies = [], []
    decision = None

    for policy_name, yaml_text in policies:
        try:
            rules = (yaml.safe_load(yaml_text) or {}).get("rules") or []
        except (yaml.YAMLError, AttributeError):
            skipped_policies.append(policy_name)
            continue
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            match = rule.get("match") or {}
            keywords, pii = match.get("keywords") or [], match.get("pii") or []
            if not keywords and not pii:
                unchecked_rules.append(rule.get("name", "unnamed-rule"))   # intent-only: nothing we can check
                continue
            evidence = [f"keyword '{k}'" for k in keywords if _has_phrase(words, k)]
            for kind in pii:
                seen = _pii_evidence(prompt, words, kind)
                if seen:
                    evidence.append(f"pii {kind} ('{seen}')")
            if evidence and decision is None:
                decision = {
                    "action": ACTIONS.get(str(rule.get("action", "DENY")).upper(), "BLOCK"),
                    "matched_policy": policy_name,
                    "matched_rule": rule.get("name", "unnamed-rule"),
                    "matched_on": evidence,
                    "message": rule.get("message", ""),
                }

    if decision is None:
        decision = {
            "action": "ALLOW",
            "matched_policy": None,
            "matched_rule": "none",
            "matched_on": [],
            "message": ("No active policy rule matched this prompt." if policies
                        else "No active policy to check against."),
        }
    return {
        **decision,
        "intent_category": "not_checked",
        "risk_score": None,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "engine": ENGINE,
        "checked": CHECKED,
        "not_checked": NOT_CHECKED,
        "policies_checked": len(policies) - len(skipped_policies),
        "unchecked_rules": unchecked_rules,
        "skipped_policies": skipped_policies,
    }
