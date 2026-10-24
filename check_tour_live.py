"""Check the live tour payload + registry for any emoji in bot fields."""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

req = urllib.request.Request("https://youthopiaos.onrender.com/api/community/tour")
live = json.loads(urllib.request.urlopen(req, timeout=30).read())

EMOJI_RANGE = (0x1F000, 0x1FAFF)

def find_emoji(text: str) -> bool:
    return any(ord(c) >= EMOJI_RANGE[0] for c in text or "")

page4 = [p for p in live["pages"] if p.get("bots")][0]
for bot in page4["bots"]:
    fields = ["name", "short", "tagline", "handle", "responsibility", "emoji"]
    flagged = {f: bot[f] for f in fields if find_emoji(bot[f]) and f != "emoji"}
    print(bot["name"], "-> payload still carries emoji fields." if flagged else "-> clean text")
    for f, v in flagged.items():
        print(f"   {f}: {v}")
    print("   (emoji field served but no longer rendered)")
