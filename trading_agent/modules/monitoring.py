"""Monitoring Module — console dashboard + Telegram alerts."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, date
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box

from trading_agent.config import NotificationConfig
from trading_agent.modules.market_analysis import MarketRegime
from trading_agent.modules.strategy_engine import TradingSignal
from trading_agent.utils.database import get_recent_trades, get_daily_pnl
from trading_agent.utils.logger import logger

console = Console()


class Monitor:
    def __init__(self, cfg: NotificationConfig):
        self.cfg = cfg
        self._telegram_available = bool(cfg.telegram_token and cfg.telegram_chat_id)

    # ── Console Dashboard ─────────────────────────────────────────────────────

    def print_regime_table(self, regimes: list[MarketRegime]) -> None:
        t = Table(title="Market Regimes", box=box.ROUNDED, show_header=True, header_style="bold cyan")
        t.add_column("Symbol")
        t.add_column("Price", justify="right")
        t.add_column("Trend")
        t.add_column("Regime")
        t.add_column("RSI", justify="right")
        t.add_column("RVOL", justify="right")
        t.add_column("VWAP", justify="right")
        for r in regimes:
            trend_style = "green" if r.trend == "bullish" else "red" if r.trend == "bearish" else "yellow"
            t.add_row(
                r.symbol,
                f"{r.current_price:.4f}",
                f"[{trend_style}]{r.trend.upper()}[/{trend_style}]",
                r.regime,
                f"{r.rsi:.1f}",
                f"{r.rvol:.2f}x",
                f"{r.vwap:.4f}",
            )
        console.print(t)

    def print_signals_table(self, signals: list[TradingSignal]) -> None:
        t = Table(title="Trading Signals", box=box.ROUNDED, header_style="bold magenta")
        t.add_column("Symbol")
        t.add_column("Direction")
        t.add_column("Confidence", justify="right")
        t.add_column("Entry Zone")
        t.add_column("Stop-Loss", justify="right")
        t.add_column("TP1 / TP2")
        t.add_column("Prob")
        for s in signals:
            if s.direction == "hold":
                continue
            dir_style = "green" if s.direction == "long" else "red"
            t.add_row(
                s.symbol,
                f"[{dir_style}]{s.direction.upper()}[/{dir_style}]",
                f"{s.confidence:.2f}",
                f"{s.entry_zone[0]:.4f} – {s.entry_zone[1]:.4f}",
                f"{s.stop_loss:.4f}",
                f"{s.take_profit_1:.4f} / {s.take_profit_2:.4f}",
                s.probability,
            )
        console.print(t)

    async def print_portfolio_summary(self, risk_status: dict) -> None:
        pnl = await get_daily_pnl(date.today().isoformat())
        pnl_style = "green" if pnl >= 0 else "red"
        console.print(Panel(
            f"[bold]Equity:[/bold] ${risk_status['equity']:,.2f}  |  "
            f"[bold]Daily PnL:[/bold] [{pnl_style}]${pnl:+,.2f}[/{pnl_style}]  |  "
            f"[bold]Drawdown:[/bold] {risk_status['drawdown_pct']:.2f}%  |  "
            f"[bold]Kill Switch:[/bold] {'🔴 ON' if risk_status['kill_switch'] else '🟢 OFF'}",
            title=f"[bold cyan]AcendARC 2.0 — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}[/bold cyan]",
            box=box.DOUBLE,
        ))

    # ── Telegram ──────────────────────────────────────────────────────────────

    async def _send_telegram(self, text: str) -> None:
        if not self._telegram_available:
            return
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{self.cfg.telegram_token}/sendMessage",
                    json={"chat_id": self.cfg.telegram_chat_id, "text": text, "parse_mode": "Markdown"},
                    timeout=10,
                )
        except Exception as exc:
            logger.warning(f"[Monitor] Telegram send failed: {exc}")

    async def alert_signal(self, signal: TradingSignal) -> None:
        msg = (
            f"📊 *AcendARC Signal*\n"
            f"Symbol: `{signal.symbol}`\n"
            f"Direction: *{signal.direction.upper()}*\n"
            f"Confidence: {signal.confidence:.2f} | Prob: {signal.probability}\n"
            f"Entry: {signal.entry_zone[0]:.4f} – {signal.entry_zone[1]:.4f}\n"
            f"SL: {signal.stop_loss:.4f} | TP1: {signal.take_profit_1:.4f}\n"
            f"_{signal.reasoning}_"
        )
        await self._send_telegram(msg)

    async def alert_kill_switch(self, reason: str) -> None:
        await self._send_telegram(f"🔴 *KILL SWITCH ACTIVATED*\nReason: {reason}")

    async def send_daily_report(self, risk_status: dict) -> None:
        trades = await get_recent_trades(limit=20)
        closed = [t for t in trades if t["status"] == "closed"]
        wins = [t for t in closed if (t["pnl"] or 0) > 0]
        win_rate = len(wins) / len(closed) * 100 if closed else 0

        msg = (
            f"📈 *Daily Report — {date.today()}*\n"
            f"Equity: ${risk_status['equity']:,.2f}\n"
            f"Daily PnL: ${risk_status['daily_pnl']:+,.2f}\n"
            f"Drawdown: {risk_status['drawdown_pct']:.2f}%\n"
            f"Win Rate (last 20): {win_rate:.0f}% ({len(wins)}/{len(closed)})\n"
        )
        await self._send_telegram(msg)
        logger.info("[Monitor] Daily report sent")
