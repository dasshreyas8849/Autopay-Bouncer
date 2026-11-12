import os
from datetime import datetime, timezone
from dotenv import load_dotenv; load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from . import data, detectors, paypal, ai

app = FastAPI()
STATE = {"findings": None, "log": []}

@app.get("/api/state")
def state():
    if STATE["findings"] is None:
        fs = detectors.detect(data.SUBS, data.TXNS, data.CHECKINS)
        for f, why in zip(fs, [ai.explain(fs).get(f["id"]) for f in fs]):
            f["reason"] = why or f["detail"]
        STATE["findings"] = fs
    return {"findings": STATE["findings"], "log": STATE["log"]}

@app.post("/api/findings/{fid}/{verdict}")
def decide(fid: str, verdict: str):
    f = next((f for f in STATE["findings"] or [] if f["id"] == fid and f["status"] == "pending"), None)
    if not f or verdict not in ("approve", "reject"):
        raise HTTPException(404, "No pending finding with that id")
    if verdict == "reject":
        f["status"] = "kept"
        return f
    s = next(s for s in data.SUBS if s["id"] == f["sub_id"])
    live = bool(s.get("paypal_id")) and bool(os.getenv("PAYPAL_CLIENT_ID"))
    try:
        if live:  # only a human click reaches this line
            getattr(paypal, f["action"])(s["paypal_id"], "Approved in Autopay Bouncer")
    except Exception as e:
        raise HTTPException(502, str(e))
    f["status"] = "done_live" if live else "done_guided"
    s["status"] = "SUSPENDED" if f["action"] == "suspend" else "CANCELLED"
    STATE["log"].append({"time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                         "what": f"{f['action']} {s['name']}", "mode": "PayPal sandbox" if live else "guided"})
    return f
@app.post("/api/undo/{fid}")
def undo(fid: str):
    f = next((f for f in STATE["findings"] or []
              if f["id"] == fid and f["status"].startswith("done") and f["action"] == "suspend"), None)
    if not f:
        raise HTTPException(404, "Nothing to undo")
    s = next(s for s in data.SUBS if s["id"] == f["sub_id"])
    live = f["status"] == "done_live"
    try:
        if live:
            paypal.activate(s["paypal_id"], "Undone in Autopay Bouncer")
    except Exception as e:
        raise HTTPException(502, str(e))
    f["status"], s["status"] = "pending", "ACTIVE"
    STATE["log"].append({"time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                         "what": f"reactivate {s['name']}", "mode": "PayPal sandbox" if live else "guided"})
    return f
app.mount("/", StaticFiles(directory="static", html=True))
