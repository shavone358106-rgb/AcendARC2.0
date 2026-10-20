"""Strategy Engine — Claude-powered market research, signal generation & backtesting."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import anthropic

from trading_agent.modules.market_analysis import MarketRegime
from trading_agent.utils.logger import logger


@dataclass
class TradingSignal:
    symbol: str
    direction: str          # "long" | "short" | "hold"
    confidence: float       # 0.0 – 3.0
    entry_zone: tuple[float, float]
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    reasoning: str
    strategy_name: str
    probability: str        # "High" | "Medium" | "Low"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_db_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "direction": self.direction,
            "confidence": self.confidence,
            "entry_zone": f"{self.entry_zone[0]:.4f}-{self.entry_zone[1]:.4f}",
            "stop_loss": self.stop_loss,
            "take_profit": json.dumps([self.take_profit_1, self.take_profit_2]),
            "reasoning": self.reasoning,
            "created_at": self.created_at,
        }


SYSTEM_PROMPT = """You are the Alpha-Quant Sentinel — an elite quantitative trading strategist.
Analyze the given market data and generate a precise trading signal.

Your output MUST be valid JSON matching this schema:
{
  "direction": "long" | "short" | "hold",
  "confidence": <float 0.0-3.0>,
  "entry_zone": [<low_price>, <high_price>],
  "stop_loss": <price>,
  "take_profit_1": <price>,
  "take_profit_2": <price>,
  "strategy_name": "<name>",
  "probability": "High" | "Medium" | "Low",
  "reasoning": "<2-3 sentence technical justification>"
}

Rules:
- NEVER output a trade without a stop_loss.
- confidence > 1.5 required to recommend long/short; otherwise output "hold".
- stop_loss must use ATR-based placement, not arbitrary round numbers.
- Probability = High if confidence >= 2.0, Medium if >= 1.5, Low otherwise.
"""


class StrategyEngine:
    def __init__(self, api_key: str, model: str = "claude-opus-5-5"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def _build_prompt(self, regime: MarketRegime) -> str:
        return f"""Market Data for {regime.symbol} ({datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}):

PRICE ACTION:
  Current Price : {regime.current_price:.4f}
  Trend         : {regime.trend.upper()}
  Regime        : {regime.regime.upper()}
  Volatility    : {regime.volatility.upper()}

TECHNICAL INDICATORS:
  RSI (14)      : {regime.rsi:.2f}
  EMA (9)       : {regime.ema9:.4f}
  EMA (20)      : {regime.ema20:.4f}
  VWAP          : {regime.vwap:.4f}
  ATR (14)      : {regime.atr:.4f}
  RVOL          : {regime.rvol:.2f}x (relative to 20-bar avg)

KEY LEVELS:
  Support       : {regime.support:.4f}
  Resistance    : {regime.resistance:.4f}

Generate a trading signal. Output ONLY valid JSON, no markdown, no commentary."""

    def generate_signal(self, regime: MarketRegime) -> TradingSignal:
        prompt = self._build_prompt(regime)
        logger.info(f"[StrategyEngine] Querying Claude for {regime.symbol}...")

        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)

        signal = TradingSignal(
            symbol=regime.symbol,
            direction=data["direction"],
            confidence=float(data["confidence"]),
            entry_zone=(float(data["entry_zone"][0]), float(data["entry_zone"][1])),
            stop_loss=float(data["stop_loss"]),
            take_profit_1=float(data["take_profit_1"]),
            take_profit_2=float(data["take_profit_2"]),
            reasoning=data["reasoning"],
            strategy_name=data.get("strategy_name", "Claude-Quant"),
            probability=data.get("probability", "Medium"),
        )
        logger.info(
            f"[StrategyEngine] {regime.symbol} → {signal.direction.upper()} | "
            f"confidence={signal.confidence:.2f} | prob={signal.probability}"
        )
        return signal

    def generate_signals(self, regimes: list[MarketRegime]) -> list[TradingSignal]:
        signals = []
        for regime in regimes:
            try:
                signals.append(self.generate_signal(regime))
            except Exception as exc:
                logger.error(f"[StrategyEngine] Failed for {regime.symbol}: {exc}")
        return signals
