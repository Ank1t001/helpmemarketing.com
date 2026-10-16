"""The Med Spa Index window rule (founder decision, 2026-10-16): each edition covers the 15th of the previous month to
the 14th of the collection month, Toronto time, both days included (28 to 31 days), so consecutive editions are
contiguous: no day is missed or counted twice. Collection happens on or after the 15th. Edition 003 (collected
15 October 2026, window 15 September to 14 October) already follows the rule. Standard library only."""
import datetime as dt


def window(collected):
    """(start, end) dates for an edition collected on `collected` (a date or ISO string)."""
    c = collected if isinstance(collected, dt.date) else dt.date.fromisoformat(str(collected)[:10])
    if c.day < 15:
        raise ValueError(f"collected on {c}: an edition is collected on or after the 15th, after its window closes on the 14th")
    end = c.replace(day=14)
    start = (end.replace(day=1) - dt.timedelta(days=1)).replace(day=15)
    return start, end
