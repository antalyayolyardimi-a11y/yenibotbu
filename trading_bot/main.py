import asyncio
import os
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import pandas as pd

from trading_bot.config import config
from trading_bot.exchange.kucoin_client import KucoinClient
from trading_bot.indicators.ta import rsi, ema, macd, atr
from trading_bot.signals.pool import Signal, SignalPool
from trading_bot.signals.scoring import score_signal, strength_from_score
from trading_bot.risk.levels import atr_levels, meets_rr
from trading_bot.utils.timeframes import ts_to_dt
from trading_bot.storage.memory import JsonStore


class Engine:
    def __init__(self):
        self.client = KucoinClient()
        self.pool = SignalPool()
        self.store = JsonStore(Path("./data/trades.json"))
        self.last_status = "Başlatılıyor..."

    def status_text(self) -> str:
        return self.last_status

    def stats_text(self) -> str:
        stats = self.store.get_stats()
        return str(stats) if stats else "İstatistik yok"

    async def scan_once(self):
        now = datetime.utcnow()
        info = []
        for symbol in config.symbols.tickers:
            try:
                ohlcv = self.client.fetch_ohlcv(symbol, timeframe=config.timeframes.entry, limit=config.data_limit)
                if not ohlcv:
                    continue
                df = pd.DataFrame(ohlcv, columns=["ts","open","high","low","close","volume"])  # type: ignore
                df["dt"] = df["ts"].apply(ts_to_dt)
                df.set_index("dt", inplace=True)

                rv = self._analyze(df)
                if rv:
                    sig = Signal(
                        symbol=symbol,
                        timeframe=config.timeframes.entry,
                        direction=rv["direction"],
                        strength=rv["strength"],
                        score=rv["score"],
                        created_at=now,
                        last_validated=now,
                        meta=rv,
                    )
                    self.pool.add(sig)
                    info.append(f"{symbol} -> {rv['direction']} {rv['strength']} skor={rv['score']:.2f}")
            except Exception as e:
                info.append(f"{symbol} hata: {e}")
        self.pool.validate(now)
        self.last_status = " | ".join(info[-5:]) if info else "Tarama tamamlandı"

    def _analyze(self, df: pd.DataFrame):
        if len(df) < 100:
            return None
        closes = df["close"]
        high = df["high"]
        low = df["low"]

        r = rsi(closes, period=config.indicators.rsi_period)
        e_fast = ema(closes, config.indicators.ema_fast)
        e_slow = ema(closes, config.indicators.ema_slow)
        m_line, m_sig, m_hist = macd(closes, config.indicators.macd_fast, config.indicators.macd_slow, config.indicators.macd_signal)
        a = atr(high, low, closes, config.indicators.atr_period)

        ema_align = int(e_fast.iloc[-1] > e_slow.iloc[-1]) - int(e_fast.iloc[-1] < e_slow.iloc[-1])
        macd_conf = int(m_hist.iloc[-1] > 0) - int(m_hist.iloc[-1] < 0)
        rsi_conf = int(r.iloc[-1] > 50) - int(r.iloc[-1] < 50)

        features = {
            "ema_alignment": ema_align,
            "macd_confluence": macd_conf,
            "rsi_confluence": rsi_conf,
            "atr_volatility": float(a.iloc[-1] / (closes.iloc[-1] + 1e-9)),
        }
        score = score_signal(features)
        strength = strength_from_score(score)

        direction = "long" if (ema_align + macd_conf + rsi_conf) > 0 else "short"
        entry = float(closes.iloc[-1])
        levels = atr_levels(entry, float(a.iloc[-1]), direction, config.indicators.atr_multiplier)
        # TP1 ile RR=1 olduğundan, RR filtresini TP2 üzerinden değerlendiriyoruz (RR≈2)
        if not meets_rr(entry, levels["sl"], levels["tp2"], config.risk.risk_reward_min):
            return None

        return {"direction": direction, "strength": strength, "score": score, "entry": entry, **levels}


async def run_engine():
    engine = Engine()
    while True:
        await engine.scan_once()
        await asyncio.sleep(30)  # 30s scan interval


if __name__ == "__main__":
    # CLI quick run: scanning only
    asyncio.run(run_engine())
