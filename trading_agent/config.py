"""Central configuration loaded from environment variables."""
from __future__ import annotations

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent


class RiskConfig(BaseModel):
    max_position_size_pct: float = Field(default=0.02)
    daily_loss_limit_pct: float = Field(default=0.05)
    max_drawdown_pct: float = Field(default=0.15)
    min_confidence: float = Field(default=1.5)
    account_size_usd: float = Field(default=10_000.0)


class ExchangeConfig(BaseModel):
    exchange_id: str = Field(default="binance")
    api_key: str = Field(default="")
    api_secret: str = Field(default="")
    sandbox: bool = Field(default=True)


class NotificationConfig(BaseModel):
    telegram_token: str = Field(default="")
    telegram_chat_id: str = Field(default="")


class AgentConfig(BaseModel):
    anthropic_api_key: str = Field(default="")
    model: str = Field(default="claude-opus-5-5")
    symbols: list[str] = Field(default_factory=lambda: ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
    log_level: str = Field(default="INFO")
    results_dir: Path = Field(default=BASE_DIR / "results")
    database_url: str = Field(default=f"sqlite+aiosqlite:///{BASE_DIR}/data/trading_agent.db")


def load_config() -> tuple[AgentConfig, ExchangeConfig, RiskConfig, NotificationConfig]:
    symbols_raw = os.getenv("SYMBOLS", "BTC/USDT,ETH/USDT,SOL/USDT")
    agent = AgentConfig(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        model=os.getenv("AI_MODEL", "claude-opus-5-5"),
        symbols=[s.strip() for s in symbols_raw.split(",")],
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        results_dir=Path(os.getenv("RESULTS_DIR", str(BASE_DIR / "results"))),
        database_url=os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/data/trading_agent.db"),
    )
    exchange = ExchangeConfig(
        exchange_id=os.getenv("EXCHANGE", "binance"),
        api_key=os.getenv("EXCHANGE_API_KEY", ""),
        api_secret=os.getenv("EXCHANGE_API_SECRET", ""),
        sandbox=os.getenv("EXCHANGE_SANDBOX", "true").lower() == "true",
    )
    risk = RiskConfig(
        max_position_size_pct=float(os.getenv("MAX_POSITION_SIZE_PCT", "0.02")),
        daily_loss_limit_pct=float(os.getenv("DAILY_LOSS_LIMIT_PCT", "0.05")),
        max_drawdown_pct=float(os.getenv("MAX_DRAWDOWN_PCT", "0.15")),
        min_confidence=float(os.getenv("MIN_CONFIDENCE", "1.5")),
        account_size_usd=float(os.getenv("ACCOUNT_SIZE_USD", "10000")),
    )
    notifications = NotificationConfig(
        telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
    )
    return agent, exchange, risk, notifications
