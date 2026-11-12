import os, time, httpx

BASE = "https://api-m.sandbox.paypal.com"
_tok = {"v": None, "exp": 0}

def token():
    if _tok["v"] and time.time() < _tok["exp"]:
        return _tok["v"]
    r = httpx.post(f"{BASE}/v1/oauth2/token", data={"grant_type": "client_credentials"},
                   auth=(os.environ["PAYPAL_CLIENT_ID"], os.environ["PAYPAL_SECRET"]), timeout=20)
    r.raise_for_status()
    d = r.json()
    _tok.update(v=d["access_token"], exp=time.time() + d["expires_in"] - 60)
    return _tok["v"]

def call(method, path, body=None):
    r = httpx.request(method, BASE + path, json=body, timeout=20,
                      headers={"Authorization": f"Bearer {token()}"})
    if r.status_code == 422:  # e.g. invalid subscription status
        raise ValueError(f"PayPal rejected the action: {r.text}")
    r.raise_for_status()
    return r.json() if r.content else {}

def suspend(sid, reason): return call("POST", f"/v1/billing/subscriptions/{sid}/suspend", {"reason": reason})
def cancel(sid, reason): return call("POST", f"/v1/billing/subscriptions/{sid}/cancel", {"reason": reason})
def activate(sid, reason): return call("POST", f"/v1/billing/subscriptions/{sid}/activate", {"reason": reason})
def transactions(sid, start, end):
    return call("GET", f"/v1/billing/subscriptions/{sid}/transactions?start_time={start}&end_time={end}")
