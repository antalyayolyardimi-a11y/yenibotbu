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
    meta: Dict = field(default_factory=dict)


class SignalPool:
    def __init__(self):
        self.pending: List[Signal] = []
        self.confirmed: List[Signal] = []

    def add(self, sig: Signal):
        self.pending.append(sig)

    def validate(self, now: datetime, min_candles: int = 3, recheck_minutes: int = 5):
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
            "pending": [s.__dict__ for s in self.pending],
            "confirmed": [s.__dict__ for s in self.confirmed],
        }
