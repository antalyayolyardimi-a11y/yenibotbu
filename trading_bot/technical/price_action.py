import pandas as pd
import numpy as np


def detect_pin_bars(df: pd.DataFrame, body_ratio: float = 0.3, wick_ratio: float = 2.0):
    """Detect pin bar / hammer / shooting star patterns"""
    open_price = df['open']
    high = df['high']
    low = df['low']
    close = df['close']
    
    # Body and wick measurements
    body_size = (close - open_price).abs()
    total_range = high - low
    upper_wick = high - np.maximum(open_price, close)
    lower_wick = np.minimum(open_price, close) - low
    
    # Pin bar criteria
    small_body = body_size < (total_range * body_ratio)
    
    # Bullish pin bar (hammer) - long lower wick
    bullish_pin = (
        small_body & 
        (lower_wick > body_size * wick_ratio) &
        (upper_wick < body_size)
    )
    
    # Bearish pin bar (shooting star) - long upper wick  
    bearish_pin = (
        small_body &
        (upper_wick > body_size * wick_ratio) &
        (lower_wick < body_size)
    )
    
    return {
        'bullish_pin': bullish_pin,
        'bearish_pin': bearish_pin,
        'body_ratio': body_size / (total_range + 1e-9),
        'upper_wick_ratio': upper_wick / (body_size + 1e-9),
        'lower_wick_ratio': lower_wick / (body_size + 1e-9)
    }


def detect_engulfing(df: pd.DataFrame):
    """Detect bullish and bearish engulfing patterns"""
    open_price = df['open']
    high = df['high']
    low = df['low']
    close = df['close']
    
    # Previous candle
    prev_open = open_price.shift(1)
    prev_high = high.shift(1)
    prev_low = low.shift(1)
    prev_close = close.shift(1)
    
    # Current and previous body direction
    current_bullish = close > open_price
    current_bearish = close < open_price
    prev_bullish = prev_close > prev_open
    prev_bearish = prev_close < prev_open
    
    # Engulfing conditions
    bullish_engulfing = (
        current_bullish & prev_bearish &
        (open_price < prev_close) &
        (close > prev_open) &
        (high > prev_high) &
        (low < prev_low)
    )
    
    bearish_engulfing = (
        current_bearish & prev_bullish &
        (open_price > prev_close) &
        (close < prev_open) &
        (high > prev_high) &
        (low < prev_low)
    )
    
    return {
        'bullish_engulfing': bullish_engulfing,
        'bearish_engulfing': bearish_engulfing
    }


def detect_support_resistance(df: pd.DataFrame, lookback: int = 20, threshold: float = 0.001):
    """Detect dynamic support and resistance levels"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    # Rolling highs and lows
    resistance = high.rolling(lookback).max()
    support = low.rolling(lookback).min()
    
    # Test if current price is near these levels
    near_resistance = (close >= resistance * (1 - threshold)) & (close <= resistance * (1 + threshold))
    near_support = (close >= support * (1 - threshold)) & (close <= support * (1 + threshold))
    
    # Breakout detection
    resistance_break = close > resistance * (1 + threshold)
    support_break = close < support * (1 - threshold)
    
    return {
        'resistance': resistance,
        'support': support,
        'near_resistance': near_resistance,
        'near_support': near_support,
        'resistance_break': resistance_break,
        'support_break': support_break
    }


def detect_structure_breaks(df: pd.DataFrame, lookback: int = 20):
    """Detect trend structure breaks with confirmation"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    # Trend highs and lows
    swing_high = high.rolling(lookback).max()
    swing_low = low.rolling(lookback).min()
    
    # Structure break conditions
    bullish_structure_break = (
        (close > swing_high.shift(1)) &  # Break above previous high
        (close.shift(1) <= swing_high.shift(2))  # Previous close was below
    )
    
    bearish_structure_break = (
        (close < swing_low.shift(1)) &  # Break below previous low
        (close.shift(1) >= swing_low.shift(2))  # Previous close was above
    )
    
    # Confirmation (price holds above/below for next candle)
    bullish_confirmed = bullish_structure_break.shift(1) & (close > swing_high.shift(2))
    bearish_confirmed = bearish_structure_break.shift(1) & (close < swing_low.shift(2))
    
    return {
        'bullish_break': bullish_structure_break,
        'bearish_break': bearish_structure_break,
        'bullish_confirmed': bullish_confirmed,
        'bearish_confirmed': bearish_confirmed,
        'swing_high': swing_high,
        'swing_low': swing_low
    }


def detect_doji(df: pd.DataFrame, body_threshold: float = 0.1):
    """Detect doji candles indicating indecision"""
    open_price = df['open']
    high = df['high']
    low = df['low']
    close = df['close']
    
    body_size = (close - open_price).abs()
    total_range = high - low
    
    # Doji: very small body relative to total range
    doji = body_size < (total_range * body_threshold)
    
    # Special doji types
    dragonfly_doji = doji & ((high - np.maximum(open_price, close)) < (total_range * 0.1))
    gravestone_doji = doji & ((np.minimum(open_price, close) - low) < (total_range * 0.1))
    
    return {
        'doji': doji,
        'dragonfly_doji': dragonfly_doji,
        'gravestone_doji': gravestone_doji,
        'body_percentage': body_size / (total_range + 1e-9)
    }


def analyze_price_action(df: pd.DataFrame):
    """Comprehensive price action analysis"""
    pin_bars = detect_pin_bars(df)
    engulfing = detect_engulfing(df)
    sr_levels = detect_support_resistance(df)
    structure = detect_structure_breaks(df)
    doji_patterns = detect_doji(df)
    
    # Combined bullish signals
    bullish_signals = (
        pin_bars['bullish_pin'] |
        engulfing['bullish_engulfing'] |
        structure['bullish_confirmed'] |
        sr_levels['support_break'].shift(1) & (df['close'] > sr_levels['support'])  # Retested support
    )
    
    # Combined bearish signals  
    bearish_signals = (
        pin_bars['bearish_pin'] |
        engulfing['bearish_engulfing'] |
        structure['bearish_confirmed'] |
        sr_levels['resistance_break'].shift(1) & (df['close'] < sr_levels['resistance'])  # Retested resistance
    )
    
    return {
        'pin_bars': pin_bars,
        'engulfing': engulfing,
        'support_resistance': sr_levels,
        'structure_breaks': structure,
        'doji': doji_patterns,
        'bullish_signals': bullish_signals,
        'bearish_signals': bearish_signals
    }