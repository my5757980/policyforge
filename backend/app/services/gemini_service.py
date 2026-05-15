import os
import re
import yaml
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))

SYSTEM_PROMPT = """You are a Lobster Trap YAML security policy generator for enterprise AI agents.
Generate ONLY valid YAML following the Lobster Trap policy schema below.
Output NOTHING except the raw YAML block — no markdown, no code fences, no explanation.

Schema:
rules:
  - name: <kebab-case-rule-name>
    match:
      intent: [list of intent strings]
      pii: [ssn, credit_card, api_key, password, medical_record, email] (optional, only if relevant)
      keywords: [list of keywords] (optional)
    action: DENY
    log: true
    message: "<human readable denial reason>"

Available intent values: data_exfiltration, prompt_injection, jailbreak, credential_theft,
unauthorized_access, pii_exposure, system_manipulation, role_confusion, harmful_content

Generate 1-3 rules that enforce the described policy. Be specific and accurate."""

CORRECTION_PROMPT = """The YAML you generated was invalid. Fix it and return ONLY valid YAML.
Previous attempt had this error: {error}
Policy description: {description}
Generate only valid YAML, no markdown fences."""

_DEMO_POLICIES = {
    "hipaa": """rules:
  - name: hipaa-phi-protection
    match:
      intent: [pii_exposure, data_exfiltration, unauthorized_access]
      pii: [medical_record, ssn, email]
      keywords: [patient, diagnosis, prescription, medical, health record, PHI, HIPAA]
    action: DENY
    log: true
    message: "HIPAA violation: Disclosure of Protected Health Information (PHI) is prohibited without explicit patient authorization."
  - name: hipaa-treatment-data-guard
    match:
      intent: [data_exfiltration, unauthorized_access]
      pii: [medical_record]
      keywords: [treatment plan, clinical notes, lab results, radiology, EHR, EMR]
    action: DENY
    log: true
    message: "HIPAA safeguard: Clinical data and treatment records cannot be accessed or transmitted outside authorized systems."
""",
    "credential": """rules:
  - name: credential-theft-prevention
    match:
      intent: [credential_theft, data_exfiltration, unauthorized_access]
      pii: [password, api_key]
      keywords: [password, secret, credentials, token, api key, private key, access key]
    action: DENY
    log: true
    message: "Security violation: Credential extraction or disclosure is strictly prohibited. All secrets must remain in secure vaults."
  - name: api-key-exposure-guard
    match:
      intent: [credential_theft, pii_exposure]
      pii: [api_key]
      keywords: [API key, bearer token, auth token, service account, oauth secret]
    action: DENY
    log: true
    message: "API key exposure blocked: Secrets must not be logged, transmitted, or embedded in responses."
""",
    "injection": """rules:
  - name: prompt-injection-block
    match:
      intent: [prompt_injection, system_manipulation, role_confusion]
      keywords: [ignore previous, disregard instructions, override policy, forget your rules, new instructions]
    action: DENY
    log: true
    message: "Prompt injection detected: Attempts to override or manipulate system instructions are blocked."
  - name: instruction-override-guard
    match:
      intent: [prompt_injection, jailbreak]
      keywords: [system prompt, you are now, pretend you are, act as if, your new role]
    action: DENY
    log: true
    message: "Instruction override attempt blocked: Agent role and policy context cannot be redefined at runtime."
""",
    "jailbreak": """rules:
  - name: jailbreak-prevention
    match:
      intent: [jailbreak, role_confusion, harmful_content]
      keywords: [DAN, do anything now, jailbreak, unrestricted mode, developer mode, god mode, no restrictions]
    action: DENY
    log: true
    message: "Jailbreak attempt detected: Requests to operate outside policy guardrails are strictly prohibited."
  - name: role-confusion-block
    match:
      intent: [role_confusion, jailbreak]
      keywords: [you have no limits, bypass safety, ignore ethics, pretend rules don't apply, fictional scenario]
    action: DENY
    log: true
    message: "Role confusion attack blocked: Agent safety policies apply universally and cannot be suspended."
""",
    "exfiltration": """rules:
  - name: data-exfiltration-block
    match:
      intent: [data_exfiltration, unauthorized_access]
      keywords: [send to external, upload to, POST to, exfiltrate, copy database, dump all records]
    action: DENY
    log: true
    message: "Data exfiltration attempt blocked: Unauthorized data transfer to external systems is prohibited."
  - name: bulk-data-transfer-guard
    match:
      intent: [data_exfiltration, unauthorized_access]
      keywords: [export all, download all, full database, all user data, bulk export, all records]
    action: DENY
    log: true
    message: "Bulk data transfer blocked: Mass data export requires explicit authorization and audit trail."
""",
    "pci": """rules:
  - name: pci-cardholder-data-protection
    match:
      intent: [pii_exposure, data_exfiltration, credential_theft]
      pii: [credit_card]
      keywords: [credit card, card number, CVV, expiry, cardholder, PAN, payment data, PCI]
    action: DENY
    log: true
    message: "PCI-DSS violation: Cardholder data cannot be logged, transmitted, or exposed outside PCI-compliant systems."
  - name: payment-processing-guard
    match:
      intent: [unauthorized_access, data_exfiltration]
      pii: [credit_card]
      keywords: [card details, billing information, payment method, stripe key, merchant account]
    action: DENY
    log: true
    message: "Payment data protected: Financial credentials and card data must remain in PCI-certified vaults."
""",
    "default": """rules:
  - name: enterprise-security-baseline
    match:
      intent: [data_exfiltration, unauthorized_access, prompt_injection]
      keywords: [internal data, confidential, proprietary, restricted, classified]
    action: DENY
    log: true
    message: "Enterprise security policy violation: Access to confidential or proprietary information requires proper authorization."
  - name: harmful-content-prevention
    match:
      intent: [harmful_content, system_manipulation, jailbreak]
      keywords: [bypass, override, ignore policy, unrestricted, no guardrails]
    action: DENY
    log: true
    message: "Harmful content or policy bypass attempt blocked: All agent interactions are governed by enterprise security policies."
""",
}


def _demo_fallback(description: str) -> tuple[str, str]:
    desc_lower = description.lower()

    if any(kw in desc_lower for kw in ["hipaa", "medical", "health", "patient", "phi", "clinical", "hospital", "doctor"]):
        key = "hipaa"
    elif any(kw in desc_lower for kw in ["pci", "credit card", "payment", "cardholder", "pan"]):
        key = "pci"
    elif any(kw in desc_lower for kw in ["credential", "password", "api key", "secret", "token", "vault"]):
        key = "credential"
    elif any(kw in desc_lower for kw in ["injection", "prompt injection", "override instruction", "ignore previous"]):
        key = "injection"
    elif any(kw in desc_lower for kw in ["jailbreak", "dan", "no restriction", "unrestricted", "bypass safety"]):
        key = "jailbreak"
    elif any(kw in desc_lower for kw in ["exfil", "exfiltrat", "external server", "send data", "leak data", "dump"]):
        key = "exfiltration"
    else:
        key = "default"

    yaml_content = _DEMO_POLICIES[key]
    name = _extract_name(yaml_content, description)
    return yaml_content, name


async def generate_policy_yaml(description: str) -> tuple[str, str]:
    """Returns (yaml_content, suggested_name). Falls back to demo policy on any Gemini error."""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=description,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.1,
                max_output_tokens=1024,
            ),
        )
        raw = response.text.strip()

        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        try:
            yaml.safe_load(raw)
            name = _extract_name(raw, description)
            return raw, name
        except yaml.YAMLError as e:
            correction = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=CORRECTION_PROMPT.format(error=str(e), description=description),
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=1024),
            )
            corrected = correction.text.strip()
            if corrected.startswith("```"):
                lines = corrected.split("\n")
                corrected = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
            yaml.safe_load(corrected)
            name = _extract_name(corrected, description)
            return corrected, name

    except Exception:
        return _demo_fallback(description)


def _extract_name(yaml_content: str, description: str) -> str:
    try:
        parsed = yaml.safe_load(yaml_content)
        rules = parsed.get("rules", [])
        if rules and isinstance(rules, list):
            return rules[0].get("name", _slug(description))
    except Exception:
        pass
    return _slug(description)


def _slug(text: str) -> str:
    return "-".join(text.lower().split()[:5]).replace(",", "").replace(".", "")
