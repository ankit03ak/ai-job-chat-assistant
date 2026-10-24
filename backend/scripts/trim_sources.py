import json
from pathlib import Path

KEEP = {"airbnb", "coinbase", "figma", "discord", "reddit", "pinterest", "gitlab",
        "asana", "dropbox", "lyft", "twilio", "instacart", "robinhood", "gusto", "cred"}

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "data" / "job_sources.json"
cfg = json.loads(p.read_text(encoding="utf-8"))
for kind in cfg:
    for s in cfg[kind]:
        s["enabled"] = s["token"] in KEEP
p.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")