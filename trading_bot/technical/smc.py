import pandas as pd


def detect_bos(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    hh = df['high'].rolling(lookback).max().shift(1)
    ll = df['low'].rolling(lookback).min().shift(1)
    bos_up = (df['close'] > hh)
    bos_down = (df['close'] < ll)
    return pd.Series(0, index=df.index).where(~(bos_up | bos_down), other=pd.Series(1, index=df.index).where(bos_up, other=-1))


def detect_choch(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    trend = df['close'].diff().rolling(lookback).mean()
    flip = trend * trend.shift(1) < 0
    return flip.astype(int)  # 1 on flip else 0


def detect_fvg(df: pd.DataFrame) -> pd.Series:
    prev_high = df['high'].shift(1)
    prev_low = df['low'].shift(1)
    gap_up = df['low'] > prev_high
    gap_down = df['high'] < prev_low
    return pd.Series(0, index=df.index).where(~(gap_up | gap_down), other=pd.Series(1, index=df.index))


def detect_order_block(df: pd.DataFrame, lookback: int = 10) -> pd.Series:
    body = (df['close'] - df['open']).abs()
    large_body = body > body.rolling(lookback).mean() * 1.5
    return large_body.astype(int)
