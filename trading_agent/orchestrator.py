"""Main Orchestrator — ties all modules together in a 24/7 loop."""
from __future__ import annotations

import asyncio
from datetime import datetime, date
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from trading_agent.config import load_config
from trading_agent.modules.market_analysis import MarketAnalyzer
from trading_agent.modules.strategy_engine import StrategyEngine
from trading_agent.modules.risk_management import RiskManager
from trading_agent.modules.trade_execution import TradeExecutor
from trading_agent.modules.monitoring import Monitor
from trading_agent.modules.self_improvement import SelfImprovement
from trading_agent.utils.database import init_db, insert_signal
from trading_agent.utils.logger import logger, setup_logger


class TradingOrchestrator:
    def __init__(self):
        self.agent_cfg, self.exchange_cfg, self.risk_cfg, self.notif_cfg = load_config()
        setup_logger(self.agent_cfg.log_level, Path("logs"))

        self.analyzer = MarketAnalyzer(self.exchange_cfg)
        self.strategy = StrategyEngine(self.agent_cfg.anthropic_api_key, self.agent_cfg.model)
        self.risk_mgr = RiskManager(self.risk_cfg)
        self.executor = TradeExecutor(self.exchange_cfg)
        self.monitor = Monitor(self.notif_cfg)
        self.improver = SelfImprovement(
            self.agent_cfg.anthropic_api_key,
            self.agent_cfg.model,
            self.agent_cfg.results_dir,
        )
        self.scheduler = AsyncIOScheduler(timezone="UTC")
        self._running = False

    # ── Core cycle ────────────────────────────────────────────────────────────

    async def run_cycle(self) -> None:
        if self.risk_mgr.kill_switch_active:
            logger.warning("[Orchestrator] Kill switch active — skipping cycle")
            return

        logger.info(f"[Orchestrator] Cycle start — {datetime.utcnow().strftime('%H:%M UTC')}")
        symbols = self.agent_cfg.symbols

        # 1. Market analysis
        try:
            regimes = await self.analyzer.analyze_all(symbols)
        except Exception as exc:
            logger.error(f"[Orchestrator] Market analysis failed: {exc}")
            return

        self.monitor.print_regime_table(regimes)

        # 2. Strategy signals
        signals = self.strategy.generate_signals(regimes)
        actionable = [s for s in signals if s.direction != "hold"]
        self.monitor.print_signals_table(signals)

        # 3. Risk sizing & execution
        for signal in actionable:
            order = self.risk_mgr.size_order(signal)
            if order is None:
                continue
            # Persist signal
            await insert_signal(signal.to_db_dict())
            # Execute
            result = await self.executor.place_order(order)
            if result:
                await self.monitor.alert_signal(signal)

        # 4. Monitor open positions (stop-loss / take-profit)
        current_prices = {r.symbol: r.current_price for r in regimes}
        await self.executor.monitor_stops(current_prices, self.risk_mgr)

        # 5. Portfolio summary
        await self.monitor.print_portfolio_summary(self.risk_mgr.status())

    # ── Scheduled tasks ───────────────────────────────────────────────────────

    async def _daily_report(self) -> None:
        await self.monitor.send_daily_report(self.risk_mgr.status())

    async def _self_review(self) -> None:
        try:
            await self.improver.run_review(self.risk_mgr.status())
        except Exception as exc:
            logger.error(f"[Orchestrator] Self-review error: {exc}")

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def start(self, interval_minutes: int = 15) -> None:
        await init_db()
        logger.info(
            f"[Orchestrator] AcendARC 2.0 starting | "
            f"symbols={self.agent_cfg.symbols} | "
            f"interval={interval_minutes}m | "
            f"sandbox={self.exchange_cfg.sandbox}"
        )

        # Schedule recurring jobs
        self.scheduler.add_job(self.run_cycle, "interval", minutes=interval_minutes, id="cycle")
        self.scheduler.add_job(self._daily_report, "cron", hour=0, minute=1, id="daily_report")
        self.scheduler.add_job(self._self_review, "cron", hour=6, minute=0, id="self_review")

        self.scheduler.start()
        self._running = True

        # Run first cycle immediately
        await self.run_cycle()

        try:
            while self._running:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            await self.stop()

    async def stop(self) -> None:
        self._running = False
        self.scheduler.shutdown(wait=False)
        await self.analyzer.close()
        await self.executor.close()
        logger.info("[Orchestrator] AcendARC 2.0 stopped.")
