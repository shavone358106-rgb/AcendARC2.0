"""SQLite async database — trades, signals, strategy log."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import aiosqlite

DB_PATH = Path(__file__).parent.parent.parent / "data" / "trading_agent.db"

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS trades (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol      TEXT    NOT NULL,
    side        TEXT    NOT NULL,
    entry_price REAL    NOT NULL,
    exit_price  REAL,
    qty         REAL    NOT NULL,
    pnl         REAL,
    status      TEXT    DEFAULT 'open',
    strategy    TEXT,
    confidence  REAL,
    stop_loss   REAL,
    take_profit REAL,
    opened_at   TEXT    NOT NULL,
    closed_at   TEXT
);

CREATE TABLE IF NOT EXISTS signals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol      TEXT    NOT NULL,
    direction   TEXT    NOT NULL,
    confidence  REAL    NOT NULL,
    entry_zone  TEXT,
    stop_loss   REAL,
    take_profit TEXT,
    reasoning   TEXT,
    created_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS strategy_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    version     INTEGER NOT NULL,
    description TEXT,
    performance TEXT,
    saved_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_stats (
    date        TEXT    PRIMARY KEY,
    total_pnl   REAL    DEFAULT 0,
    win_count   INTEGER DEFAULT 0,
    loss_count  INTEGER DEFAULT 0,
    max_drawdown REAL   DEFAULT 0,
    updated_at  TEXT
);
"""


async def init_db(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(CREATE_TABLES)
        await db.commit()


async def insert_trade(trade: dict, db_path: Path = DB_PATH) -> int:
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute(
            """INSERT INTO trades (symbol, side, entry_price, qty, strategy, confidence,
               stop_loss, take_profit, status, opened_at)
               VALUES (:symbol, :side, :entry_price, :qty, :strategy, :confidence,
                       :stop_loss, :take_profit, :status, :opened_at)""",
            trade,
        )
        await db.commit()
        return cur.lastrowid


async def close_trade(trade_id: int, exit_price: float, pnl: float, db_path: Path = DB_PATH) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "UPDATE trades SET exit_price=?, pnl=?, status='closed', closed_at=? WHERE id=?",
            (exit_price, pnl, datetime.utcnow().isoformat(), trade_id),
        )
        await db.commit()


async def insert_signal(signal: dict, db_path: Path = DB_PATH) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """INSERT INTO signals (symbol, direction, confidence, entry_zone, stop_loss,
               take_profit, reasoning, created_at)
               VALUES (:symbol, :direction, :confidence, :entry_zone, :stop_loss,
                       :take_profit, :reasoning, :created_at)""",
            signal,
        )
        await db.commit()


async def get_open_trades(db_path: Path = DB_PATH) -> list[dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM trades WHERE status='open'") as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_daily_pnl(date_str: str, db_path: Path = DB_PATH) -> float:
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            "SELECT COALESCE(SUM(pnl),0) FROM trades WHERE status='closed' AND DATE(closed_at)=?",
            (date_str,),
        ) as cur:
            row = await cur.fetchone()
    return row[0] if row else 0.0


async def get_recent_trades(limit: int = 50, db_path: Path = DB_PATH) -> list[dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM trades ORDER BY opened_at DESC LIMIT ?", (limit,)
        ) as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]
