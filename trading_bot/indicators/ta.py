import numpy as np
import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1/period, adjust=False).mean()
    roll_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = roll_up / (roll_down + 1e-9)
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()


def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k: int = 14, d: int = 3, smooth: int = 3):
    lowest_low = low.rolling(window=k).min()
    highest_high = high.rolling(window=k).max()
    stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-9)
    stoch_k = stoch_k.rolling(window=smooth).mean()
    stoch_d = stoch_k.rolling(window=d).mean()
    return stoch_k, stoch_d


def momentum(series: pd.Series, period: int = 10) -> pd.Series:
    return series - series.shift(period)


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
    """Calculate ADX, +DI, -DI"""
    prev_close = close.shift(1)
    
    # True Range
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    
    # Directional Movement
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    plus_dm = pd.Series(plus_dm, index=close.index)
    minus_dm = pd.Series(minus_dm, index=close.index)
    
    # Smoothed values
    tr_smooth = tr.ewm(alpha=1/period, adjust=False).mean()
    plus_dm_smooth = plus_dm.ewm(alpha=1/period, adjust=False).mean()
    minus_dm_smooth = minus_dm.ewm(alpha=1/period, adjust=False).mean()
    
    # DI calculations
    plus_di = 100 * plus_dm_smooth / (tr_smooth + 1e-9)
    minus_di = 100 * minus_dm_smooth / (tr_smooth + 1e-9)
    
    # ADX calculation
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-9)
    adx_value = dx.ewm(alpha=1/period, adjust=False).mean()
    
    return adx_value, plus_di, minus_di


def volume_analysis(volume: pd.Series, period: int = 20):
    """Volume analysis for Order Flow confirmation"""
    volume_sma = volume.rolling(window=period).mean()
    volume_ratio = volume / (volume_sma + 1e-9)
    
    # Volume expansion/contraction
    volume_expansion = volume_ratio > 1.2
    volume_contraction = volume_ratio < 0.8
    
    return {
        'volume_ratio': volume_ratio,
        'volume_sma': volume_sma,
        'expansion': volume_expansion,
        'contraction': volume_contraction
    }
