"""Risk Management Module — position sizing, drawdown guard, kill switch."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date

from trading_agent.config import RiskConfig
from trading_agent.modules.strategy_engine import TradingSignal
from trading_agent.utils.logger import logger


@dataclass
class SizedOrder:
    symbol: str
    side: str            # "buy" | "sell"
    qty: float
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    risk_usd: float
    confidence: float
    strategy: str


class RiskManager:
    def __init__(self, cfg: RiskConfig):
        self.cfg = cfg
        self._daily_pnl: float = 0.0
        self._peak_equity: float = cfg.account_size_usd
        self._current_equity: float = cfg.account_size_usd
        self._kill_switch: bool = False
        self._daily_date: str = date.today().isoformat()

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def kill_switch_active(self) -> bool:
        return self._kill_switch

    def update_equity(self, pnl: float) -> None:
        today = date.today().isoformat()
        if today != self._daily_date:
            self._daily_pnl = 0.0
            self._daily_date = today

        self._daily_pnl += pnl
        self._current_equity += pnl
        self._peak_equity = max(self._peak_equity, self._current_equity)
        self._check_limits()

    def _check_limits(self) -> None:
        daily_loss_limit = self.cfg.account_size_usd * self.cfg.daily_loss_limit_pct
        drawdown = (self._peak_equity - self._current_equity) / self._peak_equity

        if self._daily_pnl < -daily_loss_limit:
            logger.warning(
                f"[RiskManager] DAILY LOSS LIMIT HIT: {self._daily_pnl:.2f} USD. Kill switch ON."
            )
            self._kill_switch = True

        if drawdown > self.cfg.max_drawdown_pct:
            logger.warning(
                f"[RiskManager] MAX DRAWDOWN HIT: {drawdown*100:.1f}%. Kill switch ON."
            )
            self._kill_switch = True

    def approve_signal(self, signal: TradingSignal) -> bool:
        if self._kill_switch:
            logger.warning(f"[RiskManager] Kill switch active — blocking {signal.symbol}")
            return False
        if signal.direction == "hold":
            return False
        if signal.confidence < self.cfg.min_confidence:
            logger.info(
                f"[RiskManager] {signal.symbol} confidence {signal.confidence:.2f} < "
                f"{self.cfg.min_confidence} threshold — skip"
            )
            return False
        return True

    def size_order(self, signal: TradingSignal) -> SizedOrder | None:
        if not self.approve_signal(signal):
            return None

        entry = (signal.entry_zone[0] + signal.entry_zone[1]) / 2
        risk_per_unit = abs(entry - signal.stop_loss)
        if risk_per_unit <= 0:
            logger.warning(f"[RiskManager] {signal.symbol} — invalid stop distance, skip")
            return None

        max_risk_usd = self._current_equity * self.cfg.max_position_size_pct
        qty = max_risk_usd / risk_per_unit
        notional = qty * entry

        # Hard cap: notional can't exceed 2x max_position_size_pct of equity
        max_notional = self._current_equity * self.cfg.max_position_size_pct * 2
        if notional > max_notional:
            qty = max_notional / entry

        side = "buy" if signal.direction == "long" else "sell"

        logger.info(
            f"[RiskManager] Sized {signal.symbol} {side.upper()} qty={qty:.6f} "
            f"risk=${max_risk_usd:.2f} entry≈{entry:.4f} SL={signal.stop_loss:.4f}"
        )
        return SizedOrder(
            symbol=signal.symbol,
            side=side,
            qty=round(qty, 6),
            entry_price=entry,
            stop_loss=signal.stop_loss,
            take_profit_1=signal.take_profit_1,
            take_profit_2=signal.take_profit_2,
            risk_usd=max_risk_usd,
            confidence=signal.confidence,
            strategy=signal.strategy_name,
        )

    def status(self) -> dict:
        drawdown = (self._peak_equity - self._current_equity) / max(self._peak_equity, 1)
        return {
            "equity": round(self._current_equity, 2),
            "daily_pnl": round(self._daily_pnl, 2),
            "drawdown_pct": round(drawdown * 100, 2),
            "kill_switch": self._kill_switch,
        }
