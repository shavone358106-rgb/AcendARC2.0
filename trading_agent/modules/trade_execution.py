"""Trade Execution Module — order placement via CCXT (Binance/Bybit paper + live)."""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

import ccxt.async_support as ccxt

from trading_agent.config import ExchangeConfig
from trading_agent.modules.risk_management import SizedOrder
from trading_agent.utils.database import insert_trade, close_trade, get_open_trades
from trading_agent.utils.logger import logger


class TradeExecutor:
    def __init__(self, exchange_cfg: ExchangeConfig):
        self.cfg = exchange_cfg
        self._exchange: Optional[ccxt.Exchange] = None

    async def _get_exchange(self) -> ccxt.Exchange:
        if self._exchange is None:
            cls = getattr(ccxt, self.cfg.exchange_id)
            self._exchange = cls({
                "apiKey": self.cfg.api_key,
                "secret": self.cfg.api_secret,
                "enableRateLimit": True,
            })
            if self.cfg.sandbox:
                self._exchange.set_sandbox_mode(True)
            await self._exchange.load_markets()
        return self._exchange

    async def place_order(self, order: SizedOrder) -> dict | None:
        """Submit a market order and record it in the database."""
        try:
            ex = await self._get_exchange()
            result = await ex.create_order(
                symbol=order.symbol,
                type="market",
                side=order.side,
                amount=order.qty,
            )
            trade = {
                "symbol": order.symbol,
                "side": order.side,
                "entry_price": order.entry_price,
                "qty": order.qty,
                "strategy": order.strategy,
                "confidence": order.confidence,
                "stop_loss": order.stop_loss,
                "take_profit": order.take_profit_1,
                "status": "open",
                "opened_at": datetime.utcnow().isoformat(),
            }
            trade_id = await insert_trade(trade)
            result["_trade_id"] = trade_id
            logger.info(
                f"[Executor] Order filled — {order.symbol} {order.side.upper()} "
                f"qty={order.qty:.6f} @ ~{order.entry_price:.4f} | db_id={trade_id}"
            )
            return result
        except Exception as exc:
            logger.error(f"[Executor] Order failed for {order.symbol}: {exc}")
            return None

    async def close_position(self, trade_id: int, symbol: str, qty: float,
                              side: str, exit_price: float, pnl: float) -> None:
        """Close an open position and update the database."""
        try:
            ex = await self._get_exchange()
            close_side = "sell" if side == "buy" else "buy"
            await ex.create_order(symbol=symbol, type="market", side=close_side, amount=qty)
            await close_trade(trade_id, exit_price, pnl)
            logger.info(f"[Executor] Closed trade #{trade_id} {symbol} PnL={pnl:+.2f} USD")
        except Exception as exc:
            logger.error(f"[Executor] Close failed for trade #{trade_id}: {exc}")

    async def monitor_stops(self, current_prices: dict[str, float],
                             risk_manager) -> None:
        """Check all open trades against stop-loss and take-profit levels."""
        open_trades = await get_open_trades()
        for trade in open_trades:
            symbol = trade["symbol"]
            price = current_prices.get(symbol)
            if price is None:
                continue
            sl = trade["stop_loss"]
            tp = trade["take_profit"]
            side = trade["side"]

            hit_sl = (side == "buy" and price <= sl) or (side == "sell" and price >= sl)
            hit_tp = (side == "buy" and price >= tp) or (side == "sell" and price <= tp)

            if hit_sl or hit_tp:
                pnl = (price - trade["entry_price"]) * trade["qty"]
                if side == "sell":
                    pnl = -pnl
                await self.close_position(
                    trade["id"], symbol, trade["qty"], side, price, pnl
                )
                risk_manager.update_equity(pnl)
                tag = "TP" if hit_tp else "SL"
                logger.info(f"[Executor] {tag} triggered — {symbol} @ {price:.4f} PnL={pnl:+.4f}")

    async def close(self) -> None:
        if self._exchange:
            await self._exchange.close()
            self._exchange = None
