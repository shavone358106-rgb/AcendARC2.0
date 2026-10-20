"""Market Analysis Module — regime detection, trend, volatility, key levels."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import ccxt.async_support as ccxt
import pandas as pd
import numpy as np

from trading_agent.utils.logger import logger


@dataclass
class MarketRegime:
    symbol: str
    regime: str          # "risk_on" | "risk_off" | "neutral"
    trend: str           # "bullish" | "bearish" | "sideways"
    volatility: str      # "high" | "normal" | "low"
    rsi: float
    rvol: float          # relative volume vs 20-period avg
    vwap: float
    ema9: float
    ema20: float
    atr: float
    support: float
    resistance: float
    current_price: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class MarketAnalyzer:
    def __init__(self, exchange_cfg, timeframe: str = "15m"):
        self.exchange_cfg = exchange_cfg
        self.timeframe = timeframe
        self._exchange: Optional[ccxt.Exchange] = None

    async def _get_exchange(self) -> ccxt.Exchange:
        if self._exchange is None:
            cls = getattr(ccxt, self.exchange_cfg.exchange_id)
            self._exchange = cls({
                "apiKey": self.exchange_cfg.api_key,
                "secret": self.exchange_cfg.api_secret,
                "enableRateLimit": True,
                "options": {"defaultType": "spot"},
            })
            if self.exchange_cfg.sandbox:
                self._exchange.set_sandbox_mode(True)
        return self._exchange

    async def fetch_ohlcv(self, symbol: str, limit: int = 200) -> pd.DataFrame:
        ex = await self._get_exchange()
        raw = await ex.fetch_ohlcv(symbol, self.timeframe, limit=limit)
        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

    def _calc_vwap(self, df: pd.DataFrame) -> float:
        typical = (df["high"] + df["low"] + df["close"]) / 3
        return float((typical * df["volume"]).sum() / df["volume"].sum())

    def _calc_rvol(self, df: pd.DataFrame) -> float:
        avg_vol = df["volume"].iloc[-21:-1].mean()
        curr_vol = df["volume"].iloc[-1]
        return float(curr_vol / avg_vol) if avg_vol > 0 else 1.0

    def _key_levels(self, df: pd.DataFrame) -> tuple[float, float]:
        recent = df.tail(50)
        resistance = float(recent["high"].max())
        support = float(recent["low"].min())
        return support, resistance

    async def analyze(self, symbol: str) -> MarketRegime:
        df = await self.fetch_ohlcv(symbol)
        close = df["close"]

        # ── Indicators (pure pandas/numpy) ───────────────────────────────────
        ema9 = float(close.ewm(span=9, adjust=False).mean().iloc[-1])
        ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])

        delta = close.diff()
        gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = float(100 - (100 / (1 + rs)).iloc[-1])

        high_low = df["high"] - df["low"]
        high_prev = (df["high"] - df["close"].shift()).abs()
        low_prev = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([high_low, high_prev, low_prev], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        price = float(close.iloc[-1])
        vwap = self._calc_vwap(df)
        rvol = self._calc_rvol(df)
        support, resistance = self._key_levels(df)

        # Trend classification
        if price > ema9 > ema20:
            trend = "bullish"
        elif price < ema9 < ema20:
            trend = "bearish"
        else:
            trend = "sideways"

        # Volatility
        atr_pct = atr / price
        if atr_pct > 0.02:
            volatility = "high"
        elif atr_pct < 0.005:
            volatility = "low"
        else:
            volatility = "normal"

        # Regime (simplified — uses trend + rsi momentum)
        if trend == "bullish" and rsi < 70:
            regime = "risk_on"
        elif trend == "bearish" and rsi > 30:
            regime = "risk_off"
        else:
            regime = "neutral"

        result = MarketRegime(
            symbol=symbol,
            regime=regime,
            trend=trend,
            volatility=volatility,
            rsi=rsi,
            rvol=rvol,
            vwap=vwap,
            ema9=ema9,
            ema20=ema20,
            atr=atr,
            support=support,
            resistance=resistance,
            current_price=price,
        )
        logger.info(f"[MarketAnalysis] {symbol} → {trend.upper()} | RSI={rsi:.1f} | RVOL={rvol:.2f}x")
        return result

    async def analyze_all(self, symbols: list[str]) -> list[MarketRegime]:
        tasks = [self.analyze(s) for s in symbols]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def close(self) -> None:
        if self._exchange:
            await self._exchange.close()
            self._exchange = None
