"""Self-Improvement Module — Claude reviews performance and updates strategy notes."""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

import anthropic

from trading_agent.utils.database import get_recent_trades
from trading_agent.utils.logger import logger

BASE_DIR = Path(__file__).parent.parent.parent


REVIEW_SYSTEM = """You are a senior quantitative analyst reviewing the recent trading performance
of an autonomous trading agent. Your job is to:
1. Identify winning and losing patterns.
2. Spot weaknesses (e.g. bad stop placement, wrong regime detection).
3. Recommend SPECIFIC parameter adjustments (confidence threshold, ATR multiplier, etc).
4. Output a concise JSON report.

Output ONLY valid JSON with keys:
{
  "summary": "<2-3 sentence overall assessment>",
  "win_rate_assessment": "<observation>",
  "key_weaknesses": ["<weakness1>", "<weakness2>"],
  "recommended_adjustments": [{"parameter": "<name>", "current": "<val>", "suggested": "<val>", "reason": "<reason>"}],
  "market_regime_notes": "<observations on regime detection accuracy>"
}
"""


class SelfImprovement:
    def __init__(self, api_key: str, model: str = "claude-opus-5-5", results_dir: Path = BASE_DIR / "results"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def run_review(self, risk_status: dict) -> dict:
        trades = await get_recent_trades(limit=50)
        closed = [t for t in trades if t["status"] == "closed"]
        if not closed:
            logger.info("[SelfImprovement] No closed trades to review.")
            return {}

        wins = [t for t in closed if (t["pnl"] or 0) > 0]
        losses = [t for t in closed if (t["pnl"] or 0) <= 0]
        total_pnl = sum(t["pnl"] or 0 for t in closed)

        prompt = f"""Recent Trading Performance Review ({date.today()}):

SUMMARY STATS:
  Total closed trades : {len(closed)}
  Win count           : {len(wins)}
  Loss count          : {len(losses)}
  Win rate            : {len(wins)/len(closed)*100:.1f}%
  Total PnL           : ${total_pnl:+.2f}
  Current equity      : ${risk_status.get('equity', 0):,.2f}
  Max drawdown        : {risk_status.get('drawdown_pct', 0):.2f}%

LAST 10 TRADES (symbol | side | entry | exit | pnl | strategy):
{self._format_trades(closed[-10:])}

Please review and provide improvement recommendations."""

        logger.info("[SelfImprovement] Running Claude performance review...")
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=REVIEW_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        report = json.loads(raw)

        # Save to results directory
        fname = self.results_dir / f"review_{date.today()}.json"
        with open(fname, "w") as f:
            json.dump({"generated_at": datetime.utcnow().isoformat(), **report}, f, indent=2)
        logger.info(f"[SelfImprovement] Review saved to {fname}")
        return report

    def _format_trades(self, trades: list[dict]) -> str:
        rows = []
        for t in trades:
            rows.append(
                f"  {t['symbol']} | {t['side']} | {t['entry_price']:.4f} | "
                f"{t.get('exit_price') or 'open':>10} | "
                f"${t.get('pnl') or 0:+.2f} | {t.get('strategy','?')}"
            )
        return "\n".join(rows)
