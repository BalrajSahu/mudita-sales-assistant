import json, os
from .policy import POLICY

def qualify(data):
    # Deterministic policy engine. The LLM may extract facts, but cannot change policy.
    required = ["company_size", "decision_maker", "timeline", "budget_usd"]
    missing=[x for x in required if data.get(x) in (None, "")]
    if missing:
        return {"status":"needs_more_information","evidence":[],"missing":missing}
    size_ok = str(data["company_size"]).lower().strip() in ["10+", "10", "11+", "20+", "50+", "100+"] or (isinstance(data["company_size"], int) and data["company_size"]>=10)
    decision_ok = bool(data["decision_maker"])
    timeline_ok = str(data["timeline"]).lower() in ["within 3 months","3 months","1 month","2 months"]
    budget=float(data["budget_usd"])
    budget_ok=5000<=budget<=50000
    evidence=[f"company_size={data['company_size']}",f"decision_maker={data['decision_maker']}",f"timeline={data['timeline']}",f"budget_usd={budget}"]
    return {"status":"qualified" if all([size_ok,decision_ok,timeline_ok,budget_ok]) else "not_qualified","evidence":evidence,"missing":[]}

def route(country):
    country=(country or "").upper()
    if country in ["IN","SG","AE"]: return "rep_priya"
    return "rep_alex"
