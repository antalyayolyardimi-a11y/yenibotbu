import pandas as pd
import numpy as np


def detect_market_structure(df: pd.DataFrame, lookback: int = 20):
    """Enhanced market structure detection with HH/HL/LH/LL"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    # Higher Highs (HH) and Lower Lows (LL)
    rolling_max = high.rolling(lookback).max()
    rolling_min = low.rolling(lookback).min()
    
    hh = (high > rolling_max.shift(1))
    ll = (low < rolling_min.shift(1))
    
    # Higher Lows (HL) and Lower Highs (LH)
    hl = (low > rolling_min.shift(1)) & (low > low.rolling(lookback).min().shift(1))
    lh = (high < rolling_max.shift(1)) & (high < high.rolling(lookback).max().shift(1))
    
    # Trend structure
    structure = pd.Series(0, index=df.index)
    structure.loc[hh] = 2   # Strong bullish
    structure.loc[hl] = 1   # Bullish
    structure.loc[lh] = -1  # Bearish  
    structure.loc[ll] = -2  # Strong bearish
    
    return {
        'structure': structure,
        'hh': hh,
        'hl': hl,
        'lh': lh,
        'll': ll
    }


def detect_bos_choch(df: pd.DataFrame, lookback: int = 20):
    """Enhanced BOS/CHOCH detection"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    # Previous highs and lows
    prev_hh = high.rolling(lookback).max().shift(1)
    prev_ll = low.rolling(lookback).min().shift(1)
    
    # BOS (Break of Structure)
    bos_bullish = close > prev_hh
    bos_bearish = close < prev_ll
    
    # CHOCH (Change of Character) - trend reversal
    # Look for structure breaks after opposite trend
    trend = close.diff().rolling(lookback//2).mean()
    trend_change = (trend > 0) & (trend.shift(1) <= 0) | (trend < 0) & (trend.shift(1) >= 0)
    
    choch_bullish = bos_bullish & trend_change & (trend > 0)
    choch_bearish = bos_bearish & trend_change & (trend < 0)
    
    return {
        'bos': pd.Series(0, index=df.index).where(~(bos_bullish | bos_bearish), 
                         other=pd.Series(1, index=df.index).where(bos_bullish, other=-1)),
        'choch': pd.Series(0, index=df.index).where(~(choch_bullish | choch_bearish),
                          other=pd.Series(1, index=df.index).where(choch_bullish, other=-1)),
        'bos_bullish': bos_bullish,
        'bos_bearish': bos_bearish,
        'choch_bullish': choch_bullish,
        'choch_bearish': choch_bearish
    }


def detect_fvg(df: pd.DataFrame):
    """Enhanced Fair Value Gap detection"""
    high = df['high']
    low = df['low']
    
    # 3-candle pattern for FVG
    gap_up = (low.shift(-1) > high.shift(1))  # Current low > previous high
    gap_down = (high.shift(-1) < low.shift(1))  # Current high < previous low
    
    # FVG strength based on gap size
    gap_size_up = np.where(gap_up, low.shift(-1) - high.shift(1), 0)
    gap_size_down = np.where(gap_down, low.shift(1) - high.shift(-1), 0)
    
    return {
        'fvg_bullish': gap_up,
        'fvg_bearish': gap_down,
        'gap_size_up': pd.Series(gap_size_up, index=df.index),
        'gap_size_down': pd.Series(gap_size_down, index=df.index)
    }


def detect_order_blocks(df: pd.DataFrame, lookback: int = 10):
    """Enhanced Order Block detection"""
    open_price = df['open']
    high = df['high']
    low = df['low']
    close = df['close']
    volume = df['volume']
    
    # Body size and volume characteristics
    body_size = (close - open_price).abs()
    avg_body = body_size.rolling(lookback).mean()
    avg_volume = volume.rolling(lookback).mean()
    
    # Strong candles with high volume
    strong_bullish = (close > open_price) & (body_size > avg_body * 1.5) & (volume > avg_volume * 1.2)
    strong_bearish = (close < open_price) & (body_size > avg_body * 1.5) & (volume > avg_volume * 1.2)
    
    # Order blocks are areas where price rejected strongly
    ob_bullish = strong_bullish & (low == low.rolling(lookback).min())
    ob_bearish = strong_bearish & (high == high.rolling(lookback).max())
    
    return {
        'ob_bullish': ob_bullish,
        'ob_bearish': ob_bearish,
        'strong_bullish': strong_bullish,
        'strong_bearish': strong_bearish
    }


def detect_liquidity_zones(df: pd.DataFrame, lookback: int = 20):
    """Detect liquidity hunting zones"""
    high = df['high']
    low = df['low']
    volume = df['volume']
    
    # Areas with high volume and price rejection
    volume_avg = volume.rolling(lookback).mean()
    high_volume = volume > volume_avg * 2
    
    # Price levels where lots of stops might be
    recent_highs = high.rolling(lookback).max()
    recent_lows = low.rolling(lookback).min()
    
    # Liquidity above recent highs (buy stops)
    liquidity_above = (high >= recent_highs) & high_volume
    # Liquidity below recent lows (sell stops)  
    liquidity_below = (low <= recent_lows) & high_volume
    
    return {
        'liquidity_above': liquidity_above,
        'liquidity_below': liquidity_below,
        'high_volume_areas': high_volume
    }


def premium_discount_zones(df: pd.DataFrame, lookback: int = 50):
    """Identify premium and discount zones"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    # Range-based premium/discount
    range_high = high.rolling(lookback).max()
    range_low = low.rolling(lookback).min()
    range_mid = (range_high + range_low) / 2
    
    # Current position in range
    position_in_range = (close - range_low) / (range_high - range_low + 1e-9)
    
    premium = position_in_range > 0.7  # Upper 30% of range
    discount = position_in_range < 0.3  # Lower 30% of range
    equilibrium = (position_in_range >= 0.3) & (position_in_range <= 0.7)
    
    return {
        'premium': premium,
        'discount': discount,
        'equilibrium': equilibrium,
        'position_in_range': position_in_range
    }


# Legacy functions for compatibility
def detect_bos(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    result = detect_bos_choch(df, lookback)
    return result['bos']


def detect_choch(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    result = detect_bos_choch(df, lookback)
    return result['choch']


def detect_order_block(df: pd.DataFrame, lookback: int = 10) -> pd.Series:
    result = detect_order_blocks(df, lookback)
    return (result['ob_bullish'] | result['ob_bearish']).astype(int)
