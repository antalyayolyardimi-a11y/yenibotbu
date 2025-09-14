from pydantic import BaseModel, Field
from typing import List, Optional


class IndicatorParams(BaseModel):
    rsi_period: int = 9
    rsi_oversold: float = 35
    rsi_overbought: float = 65

    ema_fast: int = 9
    ema_slow: int = 21

    macd_fast: int = 8
    macd_slow: int = 17
    macd_signal: int = 6

    atr_period: int = 14
    atr_multiplier: float = 2.6

    stochastic_k: int = 14
    stochastic_d: int = 3
    stochastic_smooth: int = 3


class RiskParams(BaseModel):
    risk_reward_min: float = 1.5
    max_open_trades: int = 3
    risk_per_trade: float = 0.01  # 1% of equity


class Timeframes(BaseModel):
    high: str = "4h"
    mid: str = "1h"
    entry: str = "15m"
    confirm: str = "5m"


class Symbols(BaseModel):
    tickers: List[str] = Field(
        default_factory=lambda: [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "BNB/USDT",
            "XRP/USDT",
            "DOGE/USDT",
        ]
    )


class TelegramConfig(BaseModel):
    token: Optional[str] = None  # set via env
    allowed_user_ids: List[int] = Field(default_factory=list)
    chat_id: Optional[int] = None


class AppConfig(BaseModel):
    exchange: str = "kucoin"
    timeframes: Timeframes = Timeframes()
    symbols: Symbols = Symbols()
    indicators: IndicatorParams = IndicatorParams()
    risk: RiskParams = RiskParams()
    telegram: TelegramConfig = TelegramConfig()
    data_limit: int = 500  # candles to fetch


config = AppConfig()
