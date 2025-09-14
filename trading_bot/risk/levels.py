from typing import Dict
import math


def atr_levels(entry: float, atr_value: float, direction: str, atr_mult: float = 2.0):
    if direction == 'long':
        sl = entry - atr_mult * atr_value
        tp1 = entry + atr_mult * atr_value
        tp2 = entry + 2 * atr_mult * atr_value
        tp3 = entry + 3 * atr_mult * atr_value
    else:
        sl = entry + atr_mult * atr_value
        tp1 = entry - atr_mult * atr_value
        tp2 = entry - 2 * atr_mult * atr_value
        tp3 = entry - 3 * atr_mult * atr_value
    return {"sl": sl, "tp1": tp1, "tp2": tp2, "tp3": tp3}


def meets_rr(entry: float, sl: float, tp1: float, min_rr: float = 1.5) -> bool:
    risk = abs(entry - sl)
    reward = abs(tp1 - entry)
    if risk == 0:
        return False
    return reward / risk >= min_rr
