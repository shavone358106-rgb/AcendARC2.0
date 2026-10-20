#!/usr/bin/env python3
"""AcendARC 2.0 — Entry point.

Usage:
    python main.py                    # run with default 15-min interval
    python main.py --interval 5       # 5-minute cycles
    python main.py --backtest         # run self-review only (no live trading)
    python main.py --report           # print dashboard and exit
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AcendARC 2.0 Autonomous Trading Agent")
    p.add_argument("--interval", type=int, default=15, help="Cycle interval in minutes (default: 15)")
    p.add_argument("--backtest", action="store_true", help="Run self-improvement review only")
    p.add_argument("--report", action="store_true", help="Print portfolio dashboard and exit")
    p.add_argument("--once", action="store_true", help="Run a single cycle and exit")
    return p.parse_args()


async def run_backtest() -> None:
    from trading_agent.config import load_config
    from trading_agent.modules.self_improvement import SelfImprovement
    from trading_agent.utils.database import init_db
    from rich.console import Console

    await init_db()
    agent_cfg, _, _, _ = load_config()
    improver = SelfImprovement(agent_cfg.anthropic_api_key, agent_cfg.model, agent_cfg.results_dir)
    report = await improver.run_review({"equity": 10000, "drawdown_pct": 0})
    Console().print_json(__import__("json").dumps(report, indent=2))


async def run_report() -> None:
    from trading_agent.config import load_config
    from trading_agent.utils.database import init_db, get_recent_trades, get_daily_pnl
    from datetime import date
    from rich.console import Console
    from rich.table import Table
    from rich import box

    await init_db()
    trades = await get_recent_trades(limit=20)
    pnl = await get_daily_pnl(date.today().isoformat())
    console = Console()
    t = Table(title="Recent Trades", box=box.ROUNDED)
    for col in ["ID", "Symbol", "Side", "Entry", "Exit", "PnL", "Status", "Strategy"]:
        t.add_column(col)
    for tr in trades:
        pnl_str = f"${tr['pnl']:+.2f}" if tr.get("pnl") is not None else "-"
        t.add_row(
            str(tr["id"]), tr["symbol"], tr["side"],
            f"{tr['entry_price']:.4f}",
            f"{tr['exit_price']:.4f}" if tr.get("exit_price") else "-",
            pnl_str, tr["status"], tr.get("strategy") or "-",
        )
    console.print(t)
    console.print(f"\n[bold]Daily PnL:[/bold] ${pnl:+.2f}")


async def main() -> None:
    args = parse_args()

    if args.backtest:
        await run_backtest()
        return

    if args.report:
        await run_report()
        return

    from trading_agent.orchestrator import TradingOrchestrator
    agent = TradingOrchestrator()

    if args.once:
        from trading_agent.utils.database import init_db
        await init_db()
        await agent.run_cycle()
        await agent.stop()
    else:
        await agent.start(interval_minutes=args.interval)


if __name__ == "__main__":
    asyncio.run(main())
