from pydantic import BaseModel, Field
from typing import List, Optional


class IndicatorParams(BaseModel):
    # ATR and volatility
    atr_period: int = 14
    atr_multiplier: float = 1.5  # SL multiplier as per spec
    
    # ADX and trend strength
    adx_period: int = 14
    adx_min: float = 20  # minimum trend strength
    
    # Volume analysis
    volume_multiplier_min: float = 1.2  # minimum volume expansion
    volume_period: int = 20  # for volume average
    
    # Momentum indicators (for alignment, not extremes)
    rsi_period: int = 14
    rsi_min: float = 40  # minimum for bullish alignment
    rsi_max: float = 60  # maximum for bearish alignment
    
    # Legacy indicators (kept for compatibility)
    ema_fast: int = 9
    ema_slow: int = 21
    macd_fast: int = 8
    macd_slow: int = 17
    macd_signal: int = 6
    stochastic_k: int = 14
    stochastic_d: int = 3
    stochastic_smooth: int = 3


class RiskParams(BaseModel):
    # TP levels based on R multiples as per spec
    tp_r_levels: List[float] = [1.0, 1.5, 2.0]  # TP1, TP2, TP3
    sl_atr_mult: float = 1.5  # SL = entry ± (k × ATR)
    risk_reward_min: float = 1.0  # minimum R:R for signals
    max_open_trades: int = 3
    risk_per_trade: float = 0.01  # 1% of equity


class Timeframes(BaseModel):
    signal: str = "15m"    # Primary signal generation timeframe
    validation: str = "5m"  # Validation timeframe (3 candles = 15 min)
    # Legacy timeframes (kept for compatibility)
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


class SMCParams(BaseModel):
    use_bos: bool = True
    use_choch: bool = True
    use_fvg: bool = True
    use_order_block: bool = True
    
class SignalScoringParams(BaseModel):
    weights: dict = {
        "smc": 0.4,
        "volume": 0.2, 
        "trend": 0.2,
        "momentum": 0.2
    }
    
class ValidationParams(BaseModel):
    candles_5m: int = 3  # 3 candles = 15 minutes validation
    min_micro_bos: int = 1
    allow_volume_drop: bool = False

class AppConfig(BaseModel):
    exchange: str = "kucoin"
    timeframes: Timeframes = Timeframes()
    symbols: Symbols = Symbols()
    indicators: IndicatorParams = IndicatorParams()
    risk: RiskParams = RiskParams()
    smc: SMCParams = SMCParams()
    signal_scoring: SignalScoringParams = SignalScoringParams()
    validation: ValidationParams = ValidationParams()
    telegram: TelegramConfig = TelegramConfig()
    data_limit: int = 500  # candles to fetch


config = AppConfig()
