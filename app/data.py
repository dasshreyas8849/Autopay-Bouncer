from datetime import date, timedelta

ago = lambda d: (date.today() - timedelta(days=d)).isoformat()

def tx(sid, amounts, last="COMPLETED"):
    n = len(amounts)
    return [{"sub_id": sid, "date": ago(30 * (n - i)), "amount": a,
             "status": last if i == n - 1 else "COMPLETED"} for i, a in enumerate(amounts)]

# paypal_id: paste a real sandbox subscription id (from seed.py) to make approvals hit PayPal live
SUBS = [
    {"id": 1, "name": "StreamMax", "amount": 15, "category": "video", "status": "ACTIVE", "paypal_id": None},
    {"id": 2, "name": "CineBox", "amount": 12, "category": "video", "status": "ACTIVE", "paypal_id": "I-0LS0RUBEW0R6"},
    {"id": 3, "name": "TuneBox", "amount": 12, "category": "music", "status": "ACTIVE", "paypal_id": "I-EE5LKYLPNC90"},
    {"id": 4, "name": "FitPass", "amount": 30, "category": "fitness", "status": "ACTIVE", "paypal_id": None},
    {"id": 5, "name": "CloudStore", "amount": 3, "category": "storage", "status": "ACTIVE", "paypal_id": None},
    {"id": 6, "name": "Daily Brief", "amount": 5, "category": "news", "status": "ACTIVE", "paypal_id": None},
]
TXNS = (tx(1, [15, 15, 15]) + tx(2, [12, 12, 12]) + tx(3, [9, 9, 12]) +
        tx(4, [30, 30, 30]) + tx(5, [3, 3, 3], "FAILED") + tx(6, [5, 5, 5]))
CHECKINS = {1: ago(3), 3: ago(10), 4: ago(90), 6: ago(5)}  # last confirmed use

