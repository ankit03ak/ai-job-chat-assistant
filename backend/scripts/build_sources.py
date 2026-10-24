import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]

GH = "https://boards-api.greenhouse.io/v1/boards/{t}/jobs"
LV = "https://api.lever.co/v0/postings/{t}?mode=json"

GREENHOUSE = ["stripe", "airbnb", "databricks", "cloudflare", "coinbase", "figma", "discord",
              "reddit", "pinterest", "datadog", "mongodb", "elastic", "gitlab", "asana",
              "dropbox", "lyft", "twilio", "okta", "instacart", "robinhood", "brex",
              "gusto", "webflow", "razorpay", "postman"]
LEVER = ["palantir", "plaid", "cred"]


def count(kind, token):
    try:
        r = requests.get((GH if kind == "greenhouse" else LV).format(t=token), timeout=20)
        if r.status_code != 200:
            return 0
        data = r.json()
        return len(data["jobs"]) if kind == "greenhouse" else len(data)
    except Exception:
        return 0


config, total = {"greenhouse": [], "lever": []}, 0
for kind, tokens in (("greenhouse", GREENHOUSE), ("lever", LEVER)):
    for t in tokens:
        n = count(kind, t)
        print(f"{kind:10} {t:15} {n} jobs")
        if n:
            total += n
            url = f"https://boards.greenhouse.io/{t}" if kind == "greenhouse" else f"https://jobs.lever.co/{t}"
            config[kind].append({"company": t.capitalize(), "token": t, "careers_url": url, "enabled": True})

ROOT.joinpath("data", "job_sources.json").write_text(
    json.dumps(config, indent=2) + "\n", encoding="utf-8"
)
print(f"\nTotal open jobs across enabled boards: {total}")