import os
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


async def generate_policy_yaml(description: str) -> tuple[str, str]:
    """Returns (yaml_content, suggested_name). Retries once on invalid YAML."""
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
