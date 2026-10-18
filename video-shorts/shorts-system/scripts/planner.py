"""Claude API planner, used when `shorts.py make` runs outside Claude Code.
(Inside Claude Code the /shorts-system skill has Claude write these files directly,
so no API key is needed there.)

Jobs: pick segments from a long video, steal-a-hook + write a script, cold-read it with a
fresh context (the 'subagent'), dissect the script into visual moments, and review contact
sheets frame by frame."""
import base64
import json
import os
import re
from pathlib import Path

MODEL = os.environ.get("SHORTS_MODEL", "claude-opus-5-5")
PRICE_IN, PRICE_OUT = 4.0, 20.0          # $/M tokens for the default model


def available():
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
                or Path.home().joinpath(".config/anthropic").exists())


class Planner:
    def __init__(self, spend_cb=None):
        import anthropic
        self.client = anthropic.Anthropic()
        self.spend_cb = spend_cb

    def ask_json(self, system, content, effort="high"):
        resp = self.client.beta.messages.create(
            model=MODEL, max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            thinking={"type": "adaptive"}, output_config={"effort": effort},
            system=system, messages=[{"role": "user", "content": content}])
        if resp.stop_reason == "refusal":
            raise RuntimeError("Claude declined this request")
        u = resp.usage
        if self.spend_cb:
            self.spend_cb("claude-api", (u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT) / 1e6)
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        m = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.S) or re.search(r"(\{.*\})", text, re.S)
        if not m:
            raise RuntimeError(f"planner returned no JSON:\n{text[:800]}")
        return json.loads(m.group(1))

    # ------------------------------------------------------------------ segment picking
    def select_segments(self, words, topic, lane, count, target):
        lines = _timed_text(words)
        return self.ask_json(
            "You cut long videos into vertical shorts. One topic, one short: each segment must stand alone, "
            "open with a line a stranger understands cold, give a real payoff, and leave one question open.",
            f"Topic/brief: {topic or '(find the strongest standalone ideas)'}\nLane: {lane}\n"
            f"Pick {count} non-overlapping segments of about {target}s (20-45s), starting and ending on "
            f"sentence boundaries, each a different topic. Transcript with timestamps (seconds):\n{lines}\n\n"
            'Return JSON: {"segments":[{"start":s,"end":e,"topic":"...","title":"3-8 word frame-0 title that '
            'leads with what the viewer gets","why":"..."}]}')["segments"]

    # ------------------------------------------------------------------ script writing
    def write_script(self, card):
        sys = open(Path(__file__).parent.parent / "references" / "script-rules.md").read()
        draft = self.ask_json(sys, "Write the short script for this topic card:\n"
                              + json.dumps(card, indent=2) +
                              '\nReturn JSON: {"hook_versions":[{"text":"...","kept_share":0.0,"swapped":"..."}],'
                              '"script":["line 1", "..."],"title":"3-8 words","keyword_ideas":["..."]}')
        cold = self.ask_json(
            "You have never seen this project. Read the script as a stranger on first listen.",
            "Check this short script against the rules and return the fixed version.\nRules:\n" + sys +
            f"\nScript:\n{json.dumps(draft['script'])}\nCTA line must be last, word for word: {card.get('cta_line')}\n"
            'Return JSON: {"script":["..."],"changes":[{"line":n,"why":"..."}],"word_count":n}')
        draft["script"], draft["cold_read"] = cold["script"], cold.get("changes", [])
        return draft

    # ------------------------------------------------------------------ dissect (Prompt 7)
    def plan_moments(self, words, ctx, graphics_md, style_md):
        return self.ask_json(
            "You dissect locked short-video scripts into visual moments and pick graphics. "
            "Follow GRAPHICS.md exactly; it is where the creator's taste lives.\n\n" + graphics_md
            + "\n\nSTYLE.md:\n" + style_md,
            "Context:\n" + json.dumps(ctx, indent=2) + "\n\nWord timestamps (seconds):\n" + _timed_text(words, per_word=True)
            + "\n\nSplit every sentence into small visual moments. For each: start, end, job (hook, problem, claim, "
            "number, list, steps, twist, prompt, opinion, payoff, cta), text (the spoken words), the nouns you can "
            "draw, the verb (it picks the motion), graphic (one of title, statement, big_number, list, steps, "
            "before_after, prompt, cta, image, face), tone (dark/light) and data for the graphic (see GRAPHICS.md "
            "for each graphic's data fields; list/steps items carry 'at' = the second the item is spoken). "
            "Rules: frame 0 is the title graphic and holds with no cut until the first sentence ends; anything "
            "under half a second is a build step on the current graphic, never a new moment; the problem line and "
            "the 'here's the trick' line are face; claims show proof within 2s (use image only if an asset path is "
            "given, else a graphic with the real number); designed graphics split roughly 40-60% dark/light, flipping "
            "in runs on idea changes; hook and ending dark; the last moment is the cta card.\n"
            'Return JSON: {"title":"...","hook_end":s,"moments":[...],"captions":{"thing":"...","result":"...",'
            '"hashtags":["max 5"]},"cover":{"line1":"...","line2":"..."}}')

    # ------------------------------------------------------------------ QA (Prompt 6)
    def review_frames(self, sheets, plan, auto_issues):
        content = []
        for p in sheets[:8]:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                        "data": base64.b64encode(Path(p).read_bytes()).decode()}})
        content.append({"type": "text", "text":
                        "These contact sheets show the short at 3 frames per second (timestamps top-left). "
                        "Look at every frame at phone size. List each problem with its timestamp: text cut off or too "
                        "small on a phone, empty frames, a screenshot you can't read in a second, captions on top of a "
                        "graphic, something shown before it's said, beats too short to read, a cut during the hook, "
                        "text in the safe zones (top strip, bottom fifth, right edge lower half), a graphic that "
                        "doesn't match what's said.\nPlan:\n" + json.dumps(plan["moments"], indent=1) +
                        "\nAutomatic checks already found:\n" + json.dumps(auto_issues) +
                        '\nReturn JSON: {"issues":[{"time":s,"severity":"high|medium|low","problem":"..."}],'
                        '"patches":[{"moment":index,"set":{"field":"new value"}}]} — patches change plan moments '
                        "(e.g. shorter text in data, a different graphic, adjusted start/end) to fix the issues. "
                        "Empty lists if every frame earns its place."})
        return self.ask_json("You are a strict QA reviewer for vertical short videos.", content, effort="high")


def _timed_text(words, per_word=False):
    if per_word:
        return " ".join(f"{w['word']}[{w['start']:.2f}-{w['end']:.2f}]" for w in words)
    from media import sentences
    return "\n".join(f"[{s:.2f}-{e:.2f}] {t}" for s, e, t, _ in sentences(words))
