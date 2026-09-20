import os
import json
from google import genai
from google.genai import types

SYSTEM = """
You are the conversation assistant for Northstar Analytics, a fictional analytics consultancy.

Your job is ONLY to understand what the lead has said and extract facts.

Required qualification fields:
- company_size
- decision_maker
- timeline
- budget_usd
- country

Rules:
1. Extract only facts explicitly stated by the lead.
2. Never guess or invent missing information.
3. Never decide whether the lead is qualified.
4. Never invent employees, representatives, prices, policies, or routing rules.
5. If required information is missing, list it in missing_fields.
6. Ask only ONE concise follow-up question when information is missing.
7. Preserve information from earlier messages.
8. Return valid JSON only.

Return exactly this structure:

{
  "extracted_facts": {
    "company_size": null,
    "decision_maker": null,
    "timeline": null,
    "budget_usd": null,
    "country": null
  },
  "missing_fields": [],
  "reply": ""
}
"""


def analyze(messages):

    key = os.getenv("GEMINI_API_KEY")

    if not key:
        return {
            "extracted_facts": {},
            "missing_fields": [
                "company_size",
                "decision_maker",
                "timeline",
                "budget_usd",
                "country"
            ],
            "reply": (
                "Thanks for reaching out. Could you share your company size, "
                "your role in the decision, expected project timeline, "
                "approximate budget, and country?"
            )
        }

    client = genai.Client(api_key=key)

    prompt = json.dumps(messages, indent=2)

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            temperature=0,
            response_mime_type="application/json"
        )
    )

    try:
        result = json.loads(response.text)

        result.setdefault("extracted_facts", {})
        result.setdefault("missing_fields", [])
        result.setdefault("reply", "")

        return result

    except (json.JSONDecodeError, TypeError):
        return {
            "extracted_facts": {},
            "missing_fields": [
                "company_size",
                "decision_maker",
                "timeline",
                "budget_usd",
                "country"
            ],
            "reply": (
                "Could you share your company size, role, "
                "timeline, budget, and country?"
            )
        }