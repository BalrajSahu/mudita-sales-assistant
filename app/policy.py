# Editable fictional business policy for the demo.
POLICY = {
    "company": "Northstar Analytics",
    "services": ["Data analytics consulting", "Business intelligence dashboards", "Analytics automation"],
    "qualification": {
        "company_size": "10+ employees",
        "decision_maker": True,
        "timeline": "Project expected within 3 months",
        "budget_min_usd": 5000,
        "budget_max_usd": 50000,
    },
    "representatives": [
        {"id": "rep_alex", "name": "Alex", "timezone": "America/New_York", "hours": "09:00-17:00", "regions": ["US", "CA"]},
        {"id": "rep_priya", "name": "Priya", "timezone": "Asia/Kolkata", "hours": "10:00-18:00", "regions": ["IN", "SG", "AE"]},
    ],
    "routing": [
        "US/Canada leads -> Alex",
        "India/Singapore/UAE leads -> Priya",
        "Other regions -> Alex as fallback",
    ],
    "timezone": "UTC",
    "working_hours": "09:00-18:00 Monday-Friday",
}
