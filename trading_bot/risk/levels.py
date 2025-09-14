from typing import Dict, List
import math


def atr_levels(entry: float, atr_value: float, direction: str, sl_atr_mult: float = 1.5, tp_r_levels: List[float] = [1.0, 1.5, 2.0]):
    """Generate SL/TP levels based on ATR and R multiples as per specification"""
    if direction == 'long':
        sl = entry - sl_atr_mult * atr_value
        risk = sl_atr_mult * atr_value
        
        tp1 = entry + tp_r_levels[0] * risk
        tp2 = entry + tp_r_levels[1] * risk  
        tp3 = entry + tp_r_levels[2] * risk
    else:
        sl = entry + sl_atr_mult * atr_value
        risk = sl_atr_mult * atr_value
        
        tp1 = entry - tp_r_levels[0] * risk
        tp2 = entry - tp_r_levels[1] * risk
        tp3 = entry - tp_r_levels[2] * risk
        
    return {
        "sl": sl, 
        "tp1": tp1, 
        "tp2": tp2, 
        "tp3": tp3,
        "risk": risk,
        "r_multiples": tp_r_levels
    }


def meets_rr(entry: float, sl: float, tp_target: float, min_rr: float = 1.0) -> bool:
    """Check if trade meets minimum risk-reward ratio"""
    risk = abs(entry - sl)
    reward = abs(tp_target - entry)
    if risk == 0:
        return False
    return reward / risk >= min_rr


def calculate_r_multiple(entry: float, sl: float, exit_price: float) -> float:
    """Calculate R multiple for completed trade"""
    risk = abs(entry - sl)
    if risk == 0:
        return 0
    
    if (entry > sl and exit_price > entry) or (entry < sl and exit_price < entry):
        # Profitable trade
        reward = abs(exit_price - entry)
        return reward / risk
    else:
        # Loss trade  
        loss = abs(exit_price - entry)
        return -loss / risk
