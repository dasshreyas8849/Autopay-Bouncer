"""python -m app.seed  -> creates sandbox plans/subscriptions; open each approve link as a sandbox buyer."""
from dotenv import load_dotenv; load_dotenv()
from .paypal import call

for name, price in [("CineBox", "12"), ("TuneBox", "12")]:
    prod = call("POST", "/v1/catalogs/products", {"name": name, "type": "SERVICE", "category": "SOFTWARE"})
    plan = call("POST", "/v1/billing/plans", {
        "product_id": prod["id"], "name": f"{name} ${price}/mo",
        "billing_cycles": [{"frequency": {"interval_unit": "MONTH", "interval_count": 1},
                            "tenure_type": "REGULAR", "sequence": 1, "total_cycles": 0,
                            "pricing_scheme": {"fixed_price": {"value": price, "currency_code": "USD"}}}],
        "payment_preferences": {"auto_bill_outstanding": True, "payment_failure_threshold": 3}})
    sub = call("POST", "/v1/billing/subscriptions", {"plan_id": plan["id"],"application_context": {
    "brand_name": "Autopay Bouncer",
    "shipping_preference": "NO_SHIPPING",
    "user_action": "SUBSCRIBE_NOW",
    "return_url": "https://example.com/ok",
    "cancel_url": "https://example.com/no"}})
    link = next(l["href"] for l in sub["links"] if l["rel"] == "approve")
    print(f"{name}: id={sub['id']}\n  approve as buyer: {link}")
