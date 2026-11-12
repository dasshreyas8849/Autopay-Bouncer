from collections import defaultdict
from datetime import date

def detect(subs, txns, checkins):
    out, hist = [], defaultdict(list)
    for t in sorted(txns, key=lambda t: t["date"]):
        hist[t["sub_id"]].append(t)
    active = [s for s in subs if s["status"] == "ACTIVE"]

    def add(s, kind, detail, action):
        out.append({"id": f"{kind}-{s['id']}", "sub_id": s["id"], "name": s["name"], "type": kind,
                    "detail": detail, "saving": s["amount"], "action": action, "status": "pending"})

    for s in active:
        h = hist[s["id"]]
        paid = [t for t in h if t["status"] == "COMPLETED"]
        if len(paid) > 1 and paid[-1]["amount"] > paid[0]["amount"]:
            add(s, "price_hike", f"{s['name']} rose from ${paid[0]['amount']} to ${paid[-1]['amount']}.", "suspend")
        if h and h[-1]["status"] == "FAILED":
            add(s, "failed_payment", f"The last payment for {s['name']} failed.", "suspend")
        last = checkins.get(s["id"])
        if last and (date.today() - date.fromisoformat(last)).days > 60:
            add(s, "dormant", f"No use of {s['name']} since {last}.", "cancel")

    groups = defaultdict(list)
    for s in active:
        groups[s["category"]].append(s)
    for g in groups.values():
        if len(g) > 1:
            keep = max(g, key=lambda s: checkins.get(s["id"], ""))
            for s in g:
                if s is not keep:
                    add(s, "duplicate", f"{s['name']} overlaps with {keep['name']}.", "suspend")
    return out
