#!/usr/bin/env python3
"""Shorts System: one command from topic or long video to finished, QA'd short.

  shorts.py make --source long.mp4 --count 3 --lane middle --link URL   # cut a long video into shorts
  shorts.py make --recording take.mp4 --topic "..." --lane top          # your recorded/AI-twin take
  shorts.py make --topic "..." --hook "..." --hook-views N --hook-median M   # write + cold-read the script
  shorts.py approve DIR          # after YOU watched final.mp4
  shorts.py post DIR --platforms instagram,tiktok,youtube --provider ayrshare|webhook|dry-run

`make` does: cut -> trim pauses -> word timestamps -> plan (dissect) -> keyword check -> graphics ->
captions -> render -> QA every frame (fix + re-render until clean) -> captions per platform -> cover
-> STOP for your approval. It never posts on its own."""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (TEMPLATES, home, slugify, today, load_json, save_json, load_style, log_spend, die,
                    duration)
import media
import keywords as kw
from plan import enforce, heuristic_plan, write_ass, LANE_CTA
from graphics import render_moments
from render import compose
from qa import run_qa
import publish
import planner as planner_mod

PLAN_NEEDED = 3


# ---------------------------------------------------------------------------- workspace
def init_ws(ws: Path, quiet=False):
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "shorts").mkdir(exist_ok=True)
    for name in ["STYLE.md", "GRAPHICS.md", "style.json", "keywords.json", "MISTAKES.md"]:
        if not (ws / name).exists():
            shutil.copy(TEMPLATES / name, ws / name)
    if not quiet:
        print(f"workspace ready: {ws}")
    return ws


def new_short_dir(ws, topic):
    base = ws / "shorts" / f"{today()}-{slugify(topic)}"
    d, i = base, 2
    while d.exists():
        d = Path(f"{base}-{i}")
        i += 1
    d.mkdir(parents=True)
    return d


def state(d, **upd):
    s = load_json(d / "state.json", {})
    s.update(upd)
    save_json(d / "state.json", s)
    return s


def get_planner(d):
    if not planner_mod.available():
        return None
    try:
        return planner_mod.Planner(spend_cb=lambda item, usd: log_spend(d, item, usd))
    except Exception as e:                       # bad credentials etc.
        print(f"(Claude API unavailable: {e})")
        return None


# ------------------------------------------------------------------------------ stages
def stage_script(args, ws):
    """No footage yet: steal a proven hook, write the script, cold read, then STOP for 'locked'."""
    topic = args.topic or die("--topic is required to write a script")
    if args.hook_views and args.hook_median and args.hook_views < 3 * args.hook_median:
        die(f"hook views {args.hook_views} are under 3x the creator's median ({args.hook_median}). "
            "Pick a different winning hook.")
    d = Path(args.short) if args.short else new_short_dir(ws, topic)
    word, why = kw.pick(ws, topic, args.keyword, d.name)
    if not word:
        die("; ".join(why))
    cta = LANE_CTA[args.lane].format(thing=args.thing or "the guide", word=word, community=args.community)
    card = {"topic": topic, "lane": args.lane, "keyword": word, "cta_line": cta,
            "winning_hook": args.hook, "hook_source": {"link": args.hook_link, "views": args.hook_views,
                                                       "median": args.hook_median},
            "real_numbers": args.numbers, "thing": args.thing, "link": args.link}
    save_json(d / "topic_card.json", card)
    p = get_planner(d)
    if p:
        res = p.write_script(card)
        lines = res["script"]
        md = ["# Script (cold-read, NOT locked yet)", "", f"Lane: {args.lane}   Keyword: {word}", "",
              *lines, "", "## Cold-read changes", *[f"- line {c.get('line')}: {c.get('why')}" for c in res.get("cold_read", [])],
              "", "## Hook versions", *[f"- {h['text']} (kept {h.get('kept_share')})" for h in res.get("hook_versions", [])]]
        (d / "script.md").write_text("\n".join(md) + "\n")
        save_json(d / "script.json", res)
    else:
        (d / "script.md").write_text(
            f"# Script — write it here\n\nTopic card: topic_card.json\nKeyword: {word}\nLast line: {cta}\n\n"
            "Follow references/script-rules.md (hook, problem, First/Then steps, twist, list of 3, pre-CTA + CTA).\n")
    state(d, stage="script_draft", topic=topic, lane=args.lane, keyword=word)
    print(f"\nScript drafted: {d / 'script.md'}\n"
          "Read it as a stranger. When you say 'locked', record it (or render your AI twin once), then run:\n"
          f"  shorts.py make --short {d} --recording YOUR_TAKE.mp4")
    return d


def stage_cut(args, ws):
    """Long video or a single take -> one folder per short with clip.mp4 + words.json."""
    src = Path(args.source or args.recording)
    if not src.exists():
        die(f"no such file: {src}")
    dirs = []
    if args.recording:
        segs = [(args.start or 0.0, args.end or duration(src))]
        topics = [args.topic or src.stem]
        titles = [args.title]
    elif args.start is not None and args.end is not None:
        segs, topics, titles = [(args.start, args.end)], [args.topic or src.stem], [args.title]
    else:
        print("transcribing the long video to find segments...")
        tmp = ws / "cache"
        tmp.mkdir(exist_ok=True)
        wj = tmp / f"{src.stem}.words.json"
        words = media.load_words(args.words) if args.words else (media.load_words(wj) or media.transcribe(src, wj, args.model))
        p = get_planner(ws)
        if p:
            picked = p.select_segments(words, args.topic, args.lane, args.count, args.target)
            segs = [(s["start"], s["end"]) for s in picked]
            topics = [s.get("topic") or args.topic or src.stem for s in picked]
            titles = [s.get("title") for s in picked]
        else:
            segs = media.pick_segments(words, args.target, args.count)
            topics = [f"{args.topic or src.stem} {i + 1}" if args.count > 1 else (args.topic or src.stem)
                      for i in range(len(segs))]
            titles = [None] * len(segs)
        if not segs:
            die("no usable segments found; pass --start/--end")
    for (s, e), topic, title in zip(segs, topics, titles):
        d = Path(args.short) if args.short and len(segs) == 1 else new_short_dir(ws, topic)
        print(f"[{d.name}] cutting {s:.1f}-{e:.1f}s")
        raw = d / "raw.mp4"
        media.extract(src, s, e, raw)
        if args.no_trim:
            shutil.copy(raw, d / "clip.mp4")
            kept = [(0.0, e - s)]
        else:
            kept = media.trim_silence(raw, d / "clip.mp4")
            save_json(d / "trim.json", kept)
        if args.words:      # timestamps supplied (avatar/TTS tool, or a transcript of the source)
            seg_words = media.shift_words(media.load_words(args.words), s, e)
            save_json(d / "words.json", media.remap_words(seg_words, kept))
        else:
            media.transcribe(d / "clip.mp4", d / "words.json", args.model)
        prev = load_json(d / "state.json", {})
        state(d, stage="cut", source=str(src.resolve()), segment=[s, e], topic=prev.get("topic") or topic,
              title=title, lane=prev.get("lane") or args.lane, keyword=prev.get("keyword"))
        dirs.append(d)
    return dirs


def stage_build(d, args, ws):
    """Plan -> keyword -> graphics -> captions -> render -> QA loop -> captions/cover -> stop."""
    d = Path(d)
    st = load_json(d / "state.json", {})
    style = load_style(ws)
    words = media.load_words(d / "words.json")
    if not words:
        die(f"{d}/words.json is empty — no speech found")
    total = duration(d / "clip.mp4")
    topic, lane = st.get("topic") or args.topic or d.name, st.get("lane") or args.lane
    p = None

    plan = load_json(d / "plan.json")
    if plan is None or args.replan:
        if args.planner == "external":
            write_plan_request(d, ws, st, words, total, args)
            print(f"PLAN_NEEDED: write {d / 'plan.json'} (see {d / 'plan_request.md'}), then re-run the same command.")
            sys.exit(PLAN_NEEDED)
        p = get_planner(d) if args.planner in ("auto", "api") else None
        if args.planner == "api" and not p:
            die("Claude API not available (pip install anthropic and set ANTHROPIC_API_KEY)")
        ctx = {"topic": topic, "lane": lane, "title_hint": st.get("title") or args.title,
               "keyword": st.get("keyword") or args.keyword, "thing": args.thing, "link": args.link,
               "assets": args.asset or [], "duration": total}
        if p:
            print(f"[{d.name}] planning with Claude...")
            plan = p.plan_moments(words, ctx, (ws / "GRAPHICS.md").read_text(), (ws / "STYLE.md").read_text())
            plan.update({"topic": topic, "lane": lane, "planner": "claude-api"})
        else:
            print(f"[{d.name}] planning offline (heuristic)...")
            plan = heuristic_plan(words, topic, lane, ctx["keyword"], args.thing, args.link, ctx["title_hint"])
    plan.setdefault("captions", {})
    if args.link:
        plan["captions"]["link"] = args.link
    if args.thing:
        plan["captions"]["thing"] = args.thing

    word = plan.get("keyword") or st.get("keyword") or args.keyword
    if lane == "bottom":
        word = kw.load(ws).get("community_word", "CLUB")
    else:
        ok, why = kw.check(ws, word, topic, d.name) if word else (False, ["none"])
        if not ok:
            word, why = kw.pick(ws, topic, None, d.name)
            if not word:
                die("; ".join(why))
        kw.reserve(ws, word, topic, d.name)
    plan["keyword"] = word
    plan["cta_line"] = LANE_CTA[lane].format(thing=plan["captions"].get("thing") or "the guide", word=word,
                                             community=args.community)
    fixes = enforce(plan, words, total)
    save_json(d / "plan.json", plan)
    for f in fixes:
        print(f"  rule fix: {f}")

    p = p or (get_planner(d) if not args.no_vision and args.planner in ("auto", "api") else None)
    report = None
    for rnd in range(1, args.max_rounds + 1):
        print(f"[{d.name}] build round {rnd}: graphics, captions, render...")
        overlays, boxes = render_moments(plan["moments"], style, d / "graphics")
        write_ass(words, plan, style, d / "captions.ass")
        compose(d, d / "clip.mp4", plan, overlays, d / "captions.ass", style, music=args.music)
        print(f"[{d.name}] QA round {rnd}: checking every frame...")
        report = run_qa(d, d / "final.mp4", plan, words, boxes, target=style.get("target_seconds", 32))
        if p:
            review = p.review_frames(report["sheets"], plan, report["issues"])
            report["issues"] += [dict(i, source="vision") for i in review.get("issues", [])]
            patches = review.get("patches", [])
            if patches and rnd < args.max_rounds:
                for pt in patches:
                    i = pt.get("moment")
                    if isinstance(i, int) and 0 <= i < len(plan["moments"]):
                        plan["moments"][i].update(pt.get("set", {}))
                enforce(plan, words, total)
                save_json(d / "plan.json", plan)
                print(f"  applied {len(patches)} QA fix(es); re-rendering")
                continue
        break
    save_json(d / "qa" / "report.json", report)

    publish.write_captions(d, plan)
    publish.make_cover(d, d / "final.mp4", plan, ws)
    write_summary(d, plan, report)
    state(d, stage="awaiting_approval", keyword=word)
    high = [i for i in report["issues"] if i["severity"] == "high"]
    print(f"\n[{d.name}] DONE -> {d / 'final.mp4'}")
    print(f"  QA: {len(report['issues'])} issue(s), {len(high)} high — see {d / 'qa' / 'report.md'}")
    print(f"  Captions: {d / 'captions.md'}   DM: {d / 'dm.md'}   Cover: {d / 'cover.jpg'}")
    print("  Nothing posts until you watch it. Then: shorts.py approve", d)
    return report


def write_plan_request(d, ws, st, words, total, args):
    from media import sentences
    lines = "\n".join(f"[{s:.2f}-{e:.2f}] {t}" for s, e, t, _ in sentences(words))
    (d / "plan_request.md").write_text(f"""# Plan needed for {d.name}

Topic: {st.get('topic')}   Lane: {st.get('lane') or args.lane}   Length: {total:.2f}s
Keyword (reserved, may be empty): {st.get('keyword') or args.keyword or ''}
Thing the comment gets: {args.thing or ''}   Link: {args.link or ''}
Assets you may show as proof (graphic "image"): {args.asset or []}

Write plan.json in this folder. Schema and rules: references/plan-format.md and the workspace GRAPHICS.md.
Word timestamps: words.json. Sentences:

{lines}
""")


def write_summary(d, plan, report):
    md = [f"# {plan.get('title', d.name)}", "",
          f"- Lane: {plan.get('lane')}   Keyword: **{plan.get('keyword')}**   Planner: {plan.get('planner', 'external')}",
          f"- CTA: {plan.get('cta_line')}",
          f"- Video: `final.mp4` ({report['length']}s, {report['lufs']} LUFS)",
          "- Cover: `cover.jpg` (grid crop preview `cover_gridcrop.jpg`)",
          "- Captions per platform: `captions.md`   DM setup: `dm.md`",
          "- QA: `qa/report.md`, contact sheets `qa/sheet_*.jpg`", "",
          "## Moments", "", "| start | end | job | graphic | tone | text |", "|---|---|---|---|---|---|"]
    md += [f"| {m['start']:.2f} | {m['end']:.2f} | {m.get('job', '')} | {m.get('graphic')} | {m.get('tone')} | "
           f"{(m.get('text') or '')[:60]} |" for m in plan["moments"]]
    md += ["", "## Before you post", "", "Watch it on your phone with sound, start to finish. Then `shorts.py approve`."]
    (d / "SUMMARY.md").write_text("\n".join(md) + "\n")


# --------------------------------------------------------------------------------- CLI
def cmd_make(args):
    ws = init_ws(home(args.home), quiet=True)
    if args.short and (Path(args.short) / "clip.mp4").exists() and not (args.source or args.recording):
        dirs = [Path(args.short)]
    elif args.source or args.recording:
        dirs = stage_cut(args, ws)
    else:
        stage_script(args, ws)
        return
    for d in dirs:
        stage_build(d, args, ws)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--home", help="workspace (default $SHORTS_HOME or ./video-shorts/workspace)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="create the workspace (STYLE.md, GRAPHICS.md, keywords...)")

    m = sub.add_parser("make", help="the one command: topic/video -> finished, QA'd short")
    m.add_argument("--topic")
    m.add_argument("--lane", default="top", choices=["top", "middle", "bottom", "ad"])
    m.add_argument("--source", help="long video to cut shorts from")
    m.add_argument("--recording", help="your recorded take / AI-twin render of the locked script")
    m.add_argument("--start", type=float)
    m.add_argument("--end", type=float)
    m.add_argument("--count", type=int, default=1, help="shorts to cut from --source (one topic each)")
    m.add_argument("--target", type=float, default=32)
    m.add_argument("--title", help="frame-0 title (3-8 words)")
    m.add_argument("--keyword")
    m.add_argument("--thing", help="what the comment gets, e.g. 'the free setup guide'")
    m.add_argument("--link")
    m.add_argument("--community", default="the community")
    m.add_argument("--asset", action="append", help="screenshot/product image to show as proof (repeatable)")
    m.add_argument("--music", help="music bed (sits well below the voice)")
    m.add_argument("--words", help="word timestamps JSON [{word,start,end}] instead of transcribing")
    m.add_argument("--model", default="base", help="whisper model size")
    m.add_argument("--short", help="existing short folder to continue/rebuild")
    m.add_argument("--planner", default="auto", choices=["auto", "api", "heuristic", "external"],
                   help="external = stop so Claude Code writes plan.json (the skill does this)")
    m.add_argument("--replan", action="store_true")
    m.add_argument("--no-trim", action="store_true", help="keep pauses")
    m.add_argument("--no-vision", action="store_true", help="skip the Claude vision QA pass")
    m.add_argument("--max-rounds", type=int, default=3)
    m.add_argument("--hook", help="a proven hook, word for word")
    m.add_argument("--hook-link")
    m.add_argument("--hook-views", type=int)
    m.add_argument("--hook-median", type=int)
    m.add_argument("--numbers", help="your real numbers + where each one is from")

    b = sub.add_parser("build", help="re-render + QA a short after editing plan.json")
    b.add_argument("short")
    b.add_argument("--music")
    b.add_argument("--max-rounds", type=int, default=1)
    b.add_argument("--no-vision", action="store_true")

    a = sub.add_parser("approve", help="you watched final.mp4 and say go")
    a.add_argument("short")
    a.add_argument("--note", default="")

    p = sub.add_parser("post", help="schedule an APPROVED short")
    p.add_argument("short")
    p.add_argument("--platforms", default="instagram,facebook,tiktok,youtube")
    p.add_argument("--provider", default="dry-run", choices=["dry-run", "ayrshare", "webhook"])
    p.add_argument("--at", help="ISO time; default = next free morning slot (one post a day)")
    p.add_argument("--media-url", help="public URL of final.mp4 (ayrshare)")

    k = sub.add_parser("keyword", help="check / reserve / retire comment keywords")
    k.add_argument("action", choices=["check", "reserve", "retire", "suggest", "list"])
    k.add_argument("word", nargs="?")
    k.add_argument("--topic", default="")

    sub.add_parser("status", help="list shorts and their stage")
    q = sub.add_parser("qa", help="re-run QA on a short")
    q.add_argument("short")

    args = ap.parse_args()
    ws = home(args.home)

    if args.cmd == "init":
        init_ws(ws)
    elif args.cmd == "make":
        cmd_make(args)
    elif args.cmd == "build":
        ns = argparse.Namespace(planner="heuristic", replan=False, topic=None, lane="top", title=None, keyword=None,
                                thing=None, link=None, community="the community", asset=None, music=args.music,
                                max_rounds=args.max_rounds, no_vision=args.no_vision)
        stage_build(Path(args.short), ns, init_ws(ws, quiet=True))
    elif args.cmd == "approve":
        rec = publish.approve(args.short, args.note)
        print(f"approved {args.short} at {rec['approved_at']} (sha256 {rec['final_sha256'][:12]}...)")
        state(Path(args.short), stage="approved")
    elif args.cmd == "post":
        plats = [x.strip() for x in args.platforms.split(",") if x.strip()]
        bad = [x for x in plats if x not in publish.ALL_PLATFORMS]
        if bad:
            die(f"unknown platform(s) {bad}; use {publish.ALL_PLATFORMS}")
        slot, res = publish.post(args.short, ws, plats, args.provider, args.at, args.media_url)
        for r in res:
            print(f"  {r['platform']}: {r['status']}")
        print(f"slot: {slot}")
        state(Path(args.short), stage="scheduled" if args.provider != "dry-run" else "approved", slot=slot)
    elif args.cmd == "keyword":
        init_ws(ws, quiet=True)
        if args.action == "check":
            ok, why = kw.check(ws, args.word or die("word required"), args.topic)
            print("OK" if ok else "REJECTED: " + "; ".join(why))
            if not ok:
                print("try:", ", ".join(w for w in kw.suggest(args.topic or args.word) if kw.check(ws, w, args.topic)[0]))
        elif args.action == "reserve":
            ok, why = kw.check(ws, args.word, args.topic)
            if not ok:
                die("; ".join(why))
            kw.reserve(ws, args.word, args.topic)
            print(f"reserved {args.word.upper()}")
        elif args.action == "retire":
            kw.retire(ws, args.word)
            print(f"retired {args.word.upper()}")
        elif args.action == "suggest":
            print(", ".join(w for w in kw.suggest(args.topic or args.word or "") if kw.check(ws, w, args.topic)[0]))
        else:
            import json
            print(json.dumps(kw.load(ws), indent=2))
    elif args.cmd == "status":
        for d in sorted((ws / "shorts").glob("*")) if (ws / "shorts").exists() else []:
            s = load_json(d / "state.json", {})
            spend = sum(r["usd"] for r in load_json(d / "spend.json", []))
            print(f"{d.name:55s} {s.get('stage', '?'):18s} {s.get('keyword') or '':10s} ${spend:.2f}")
    elif args.cmd == "qa":
        d = Path(args.short)
        from graphics import render_moments as rm
        plan = load_json(d / "plan.json")
        _, boxes = rm(plan["moments"], load_style(ws), d / "graphics")
        r = run_qa(d, d / "final.mp4", plan, media.load_words(d / "words.json"), boxes)
        print((d / "qa" / "report.md").read_text())


if __name__ == "__main__":
    main()
