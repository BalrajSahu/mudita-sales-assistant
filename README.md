# Northstar Analytics — Assignment 01

Focused prototype: incoming inquiries → qualification → routing → calendar booking → human control.

## Stack
- FastAPI + SQLite
- Jinja2 minimal UI
- OpenAI-compatible LLM via server-side API key
- Google Calendar API adapter (OAuth/freebusy/events.insert)
- Meta webhook endpoints for Instagram/WhatsApp

## Run
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```
Open http://localhost:8000.

## Policy
Edit `app/policy.py`. The LLM extracts facts only; qualification/routing is deterministic and policy-driven.

## Integration notes
Google Calendar should use OAuth server-side credentials and `freebusy.query` to read availability, then re-check immediately before `events.insert`. Gmail can use Gmail API messages/watch; Meta uses webhooks for WhatsApp/Instagram. Provider setup must be performed with owned test accounts.

## Known limitations
The included first pass intentionally does not claim the provider integrations are complete. Connect credentials and implement provider-specific parsing/send adapters before demoing them as real integrations. Add webhook signature verification, OAuth token storage/refresh, outbound channel senders, and booking idempotency handling as the next implementation steps.
