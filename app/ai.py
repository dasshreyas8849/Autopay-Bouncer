import os, json, httpx

def explain(findings):
    """The model only writes explanations. It has no tools and cannot touch money."""
    fallback = {f["id"]: f["detail"] for f in findings}
    base, key = os.getenv("LLM_BASE_URL", ""), os.getenv("LLM_API_KEY", "")
    if not findings or not base:
        return fallback
    try:
        r = httpx.post(base.rstrip("/") + "/chat/completions", timeout=60,
            headers={"Authorization": f"Bearer {key or 'none'}"},
            json={"model": os.environ["LLM_MODEL"], "messages": [
                {"role": "system", "content":
                    "For each subscription finding, write 1-2 plain, friendly sentences saying why it "
                    'matters and what you suggest. Reply with only JSON: {"<finding id>": "<text>"}.'},
                {"role": "user", "content": json.dumps(findings)}]})
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip().strip("`").removeprefix("json").strip()
        return {**fallback, **json.loads(text)}
    except Exception as e:
        print("AI call failed, using plain text instead:", e)
        return fallback