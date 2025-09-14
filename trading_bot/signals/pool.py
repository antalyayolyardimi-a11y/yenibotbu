from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta


@dataclass
class Signal:
    symbol: str
    timeframe: str
    direction: str  # 'long' or 'short'
    strength: str   # 'WEAK'|'MID'|'STRONG'
    score: float
    created_at: datetime
    last_validated: datetime
    candles_confirmed: int = 0
    is_confirmed: bool = False
    meta: Dict = field(default_factory=dict)


class SignalPool:
    def __init__(self):
        self.pending: List[Signal] = []
        self.confirmed: List[Signal] = []

    def add(self, sig: Signal):
        """Add new signal to pending pool"""
        self.pending.append(sig)

    def get_pending_signals(self) -> List[Signal]:
        """Get all pending signals for validation"""
        return self.pending.copy()
        
    def get_confirmed_signals(self) -> List[Signal]:
        """Get all confirmed signals"""
        return self.confirmed.copy()
        
    def confirm_signal(self, symbol: str, direction: str):
        """Move signal from pending to confirmed"""
        for i, signal in enumerate(self.pending):
            if signal.symbol == symbol and signal.direction == direction:
                signal.is_confirmed = True
                confirmed_signal = self.pending.pop(i)
                self.confirmed.append(confirmed_signal)
                return confirmed_signal
        return None
        
    def remove_expired_signals(self, max_age_minutes: int = 60):
        """Remove old signals that haven't been confirmed"""
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=max_age_minutes)
        
        self.pending = [s for s in self.pending if s.created_at > cutoff]
        self.confirmed = [s for s in self.confirmed if s.created_at > cutoff]

    def validate(self, now: datetime, min_candles: int = 3, recheck_minutes: int = 5):
        """Legacy validation method for compatibility"""
        still_pending: List[Signal] = []
        for s in self.pending:
            if (now - s.last_validated).total_seconds() >= recheck_minutes * 60:
                s.candles_confirmed += 1
                s.last_validated = now
            if s.candles_confirmed >= min_candles:
                self.confirmed.append(s)
            else:
                still_pending.append(s)
        self.pending = still_pending

    def snapshot(self):
        return {
            "pending": len(self.pending),
            "confirmed": len(self.confirmed),
            "pending_details": [
                {
                    "symbol": s.symbol,
                    "direction": s.direction,
                    "strength": s.strength,
                    "score": f"{s.score:.2f}",
                    "age_min": int((datetime.utcnow() - s.created_at).total_seconds() / 60)
                } for s in self.pending
            ],
            "confirmed_details": [
                {
                    "symbol": s.symbol, 
                    "direction": s.direction,
                    "strength": s.strength,
                    "score": f"{s.score:.2f}",
                    "age_min": int((datetime.utcnow() - s.created_at).total_seconds() / 60)
                } for s in self.confirmed
            ]
        }
