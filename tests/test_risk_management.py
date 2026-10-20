"""Unit tests for the Risk Management module."""
import pytest
from trading_agent.config import RiskConfig
from trading_agent.modules.risk_management import RiskManager
from trading_agent.modules.strategy_engine import TradingSignal


def make_signal(direction="long", confidence=2.0, entry=(100.0, 102.0), sl=97.0, tp1=108.0, tp2=115.0):
    return TradingSignal(
        symbol="BTC/USDT",
        direction=direction,
        confidence=confidence,
        entry_zone=entry,
        stop_loss=sl,
        take_profit_1=tp1,
        take_profit_2=tp2,
        reasoning="test",
        strategy_name="test",
        probability="High",
    )


def make_rm(account=10_000.0, max_pos=0.02, daily_limit=0.05, max_dd=0.15, min_conf=1.5):
    cfg = RiskConfig(
        account_size_usd=account,
        max_position_size_pct=max_pos,
        daily_loss_limit_pct=daily_limit,
        max_drawdown_pct=max_dd,
        min_confidence=min_conf,
    )
    return RiskManager(cfg)


class TestApproveSignal:
    def test_approves_valid_long(self):
        rm = make_rm()
        assert rm.approve_signal(make_signal()) is True

    def test_rejects_hold(self):
        rm = make_rm()
        assert rm.approve_signal(make_signal(direction="hold")) is False

    def test_rejects_low_confidence(self):
        rm = make_rm(min_conf=1.5)
        assert rm.approve_signal(make_signal(confidence=1.2)) is False

    def test_rejects_when_kill_switch(self):
        rm = make_rm()
        rm._kill_switch = True
        assert rm.approve_signal(make_signal()) is False


class TestSizeOrder:
    def test_size_uses_max_risk_pct(self):
        rm = make_rm(account=10_000, max_pos=0.02)
        signal = make_signal(entry=(100.0, 102.0), sl=97.0)
        order = rm.size_order(signal)
        assert order is not None
        entry = 101.0
        risk_per_unit = abs(entry - 97.0)
        max_risk = 10_000 * 0.02
        expected_qty = max_risk / risk_per_unit
        assert abs(order.qty - expected_qty) < 0.001

    def test_returns_none_for_zero_stop_distance(self):
        rm = make_rm()
        signal = make_signal(entry=(100.0, 100.0), sl=100.0)
        assert rm.size_order(signal) is None

    def test_returns_none_when_kill_switch(self):
        rm = make_rm()
        rm._kill_switch = True
        assert rm.size_order(make_signal()) is None


class TestDrawdownKillSwitch:
    def test_kill_switch_on_max_drawdown(self):
        rm = make_rm(account=10_000, max_dd=0.15)
        rm.update_equity(-1_600)  # 16% drawdown
        assert rm.kill_switch_active is True

    def test_kill_switch_on_daily_loss(self):
        rm = make_rm(account=10_000, daily_limit=0.05)
        rm.update_equity(-600)  # 6% daily loss
        assert rm.kill_switch_active is True

    def test_no_kill_switch_within_limits(self):
        rm = make_rm(account=10_000, daily_limit=0.05, max_dd=0.15)
        rm.update_equity(-400)  # 4% — within both limits
        assert rm.kill_switch_active is False
