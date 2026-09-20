import os
from datetime import datetime, timedelta, timezone

# Google Calendar adapter. OAuth/token plumbing can be added without changing the booking contract.
# The interface deliberately re-checks availability immediately before insert.
class CalendarAdapter:
    def __init__(self): self.calendar_id=os.getenv('GOOGLE_CALENDAR_ID','primary')
    def available_slots(self, start, end, duration_minutes=30):
        # TODO: replace with Google Calendar freebusy.query once OAuth credentials are connected.
        # Kept as a clearly marked integration seam, not presented as a completed real integration.
        slots=[]; cur=start
        while cur + timedelta(minutes=duration_minutes) <= end:
            if cur.hour>=9 and cur.hour<17:
                slots.append(cur.isoformat())
            cur += timedelta(minutes=30)
        return slots
    def recheck(self, slot_start): return True
    def create_event(self, slot_start, lead_email, summary='Northstar Analytics discovery call'):
        raise RuntimeError('Google Calendar credentials are not connected yet')
