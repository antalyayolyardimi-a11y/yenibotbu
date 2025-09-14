import pandas as pd


def volume_poc(df: pd.DataFrame, bins: int = 24) -> pd.Series:
    # Very rough POC: rolling window bin with max volume
    rolling = df['volume'].rolling(bins).apply(lambda x: x.idxmax() if len(x.dropna()) else 0, raw=False)
    return rolling


def volume_anomaly(df: pd.DataFrame, lookback: int = 50, threshold: float = 2.0) -> pd.Series:
    ma = df['volume'].rolling(lookback).mean()
    std = df['volume'].rolling(lookback).std()
    z = (df['volume'] - ma) / (std + 1e-9)
    return (z > threshold).astype(int)
