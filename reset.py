from dotenv import load_dotenv; load_dotenv()
from app import data, paypal

for s in data.SUBS:
    if s.get("paypal_id"):
        try:
            paypal.activate(s["paypal_id"], "reset")
            print("reactivated", s["name"])
        except Exception as e:
            print(s["name"], "- already active or error:", str(e)[:80])