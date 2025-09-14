from typing import Dict


def score_signal(features: Dict) -> float:
    score = 0.0
    score += features.get('rsi_confluence', 0) * 1.0
    score += features.get('macd_confluence', 0) * 1.0
    score += features.get('ema_alignment', 0) * 0.8
    score += features.get('atr_volatility', 0) * 0.5
    score += features.get('smc_bos', 0) * 1.0
    score += features.get('smc_choch', 0) * 0.8
    score += features.get('fvg', 0) * 0.6
    score += features.get('volume_anomaly', 0) * 0.7
    return score


def strength_from_score(score: float) -> str:
    if score >= 3.5:
        return 'STRONG'
    if score >= 2.0:
        return 'MID'
    return 'WEAK'
