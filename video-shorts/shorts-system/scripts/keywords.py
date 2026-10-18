"""Comment-to-DM keyword registry (Prompt 8). A trigger word nobody else uses:
checked against reserved/retired words, your DM automations, recent captions and
common words people type anyway. Never reuse a retired word."""
import re
from pathlib import Path

from common import load_json, save_json, today

COMMON = set("""yes no yep love info link links me pls please send want need more help hi hello hey
wow nice cool great good amazing thanks thank ty fire lit lol omg ok okay same this that it here
guide free price how what why who when where now dm details course video full lesson tips""".split())


def registry_path(ws):
    return Path(ws) / "keywords.json"


def load(ws):
    return load_json(registry_path(ws), {"reserved": [], "retired": [], "automations": [], "community_word": "CLUB"})


def check(ws, word, topic="", short=""):
    """Return (ok, reasons)."""
    reg = load(ws)
    w = word.strip().upper()
    reasons = []
    if not re.fullmatch(r"[A-Z]{3,10}", w):
        reasons.append("use 3-10 letters, no spaces/numbers/symbols")
    if w.lower() in COMMON:
        reasons.append("a common word people type anyway")
    if re.search(r"(PH|GH|OUGH|EIGH|PS|KN|WR|QU)", w) or re.search(r"(.)\1\1", w):
        reasons.append("hard to spell after hearing it once")
    taken = {r["word"]: r for r in reg["reserved"]}
    mine = w in taken and ((short and taken[w].get("short") == short) or taken[w].get("topic") == topic)
    if w in taken and not mine:
        reasons.append(f"already reserved for '{taken[w].get('topic')}' on {taken[w].get('date')}")
    if w in {r["word"] for r in reg["retired"]}:
        reasons.append("retired; never reuse a retired word")
    if w in {a.upper() for a in reg.get("automations", [])}:
        reasons.append("used by one of your DM automations")
    if w == reg.get("community_word", "").upper() and topic and "bottom" not in topic:
        reasons.append("this is your fixed bottom-lane community word")
    shorts = Path(ws) / "shorts"
    if shorts.exists():
        for cap in sorted(shorts.glob("*/captions.md"))[-30:]:
            if cap.parent.name == short:
                continue
            if re.search(rf'comment\s+"?{w}"?\b', cap.read_text(), re.I) and not mine:
                reasons.append(f"used in recent post captions ({cap.parent.name})")
                break
    return (not reasons), reasons


def suggest(topic, n=8):
    words = [x.upper() for x in re.findall(r"[a-zA-Z]{3,10}", topic) if x.lower() not in COMMON]
    out = []
    for x in words:
        out += [x, x[:6]]
    out += [w + "X" for w in words[:2]] + ["BUILD", "STACK", "BLUEPRINT"[:9], "SHIP", "PLAYBOOK"[:8]]
    seen, res = set(), []
    for x in out:
        if x not in seen and 3 <= len(x) <= 10:
            seen.add(x)
            res.append(x)
    return res[:n]


def reserve(ws, word, topic, short=""):
    reg = load(ws)
    w = word.upper()
    reg["reserved"] = [r for r in reg["reserved"] if r["word"] != w]
    reg["reserved"].append({"word": w, "topic": topic, "short": short, "date": today()})
    save_json(registry_path(ws), reg)


def retire(ws, word):
    reg = load(ws)
    w = word.upper()
    reg["reserved"] = [r for r in reg["reserved"] if r["word"] != w]
    reg["retired"].append({"word": w, "date": today()})
    save_json(registry_path(ws), reg)


def pick(ws, topic, wanted=None, short=""):
    """Reserve `wanted` if it passes, otherwise the first suggestion that passes."""
    for w in ([wanted] if wanted else []) + suggest(topic):
        ok, why = check(ws, w, topic, short)
        if ok:
            reserve(ws, w, topic, short)
            return w.upper(), []
        if w == wanted:
            print(f"keyword {w} rejected: {'; '.join(why)}")
    return None, ["no candidate passed; pass --keyword"]
