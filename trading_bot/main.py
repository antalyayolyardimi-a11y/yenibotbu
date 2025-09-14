import asyncio
import os
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import pandas as pd

from trading_bot.config import config
from trading_bot.exchange.kucoin_client import KucoinClient
from trading_bot.indicators.ta import rsi, ema, macd, atr, adx, volume_analysis
from trading_bot.technical.smc import detect_bos_choch, detect_fvg, detect_order_blocks, premium_discount_zones
from trading_bot.technical.price_action import analyze_price_action
from trading_bot.signals.pool import Signal, SignalPool
from trading_bot.signals.scoring import score_signal, strength_from_score
from trading_bot.risk.levels import atr_levels, meets_rr
from trading_bot.trading.tracker import Trade, TradeTracker, TradeDirection
from trading_bot.utils.timeframes import ts_to_dt
from trading_bot.storage.memory import JsonStore


class Engine:
    def __init__(self):
        self.client = KucoinClient()
        self.pool = SignalPool()
        self.tracker = TradeTracker()
        self.store = JsonStore(Path("./data/trades.json"))
        self.last_status = "Başlatılıyor..."

    def status_text(self) -> str:
        return self.last_status

    def stats_text(self) -> str:
        trade_summary = self.tracker.get_trade_summary()
        return f"""📊 Bot İstatistikleri:
Aktif: {trade_summary['active_trades']} | Tamamlanan: {trade_summary['completed_trades']}
Kazanan: {trade_summary['winners']} | Başarı: %{trade_summary['win_rate']:.1f}
Toplam P&L: %{trade_summary['total_pnl']:.2f}"""

    async def scan_once(self):
        """Main scanning loop - 15m signal generation + 5m validation"""
        now = datetime.utcnow()
        info = []
        
        # Update active trades with current prices
        current_prices = {}
        for symbol in config.symbols.tickers:
            try:
                # Get current price for trade tracking
                ohlcv_current = self.client.fetch_ohlcv(symbol, timeframe="1m", limit=1)
                if ohlcv_current:
                    current_prices[symbol] = float(ohlcv_current[0][4])  # close price
            except:
                pass
        
        # Update trade tracker
        updated_trades = self.tracker.update_prices(current_prices)
        
        # Process 15m signal generation
        for symbol in config.symbols.tickers:
            try:
                # Fetch 15m data for signal generation
                ohlcv_15m = self.client.fetch_ohlcv(symbol, timeframe=config.timeframes.signal, limit=config.data_limit)
                if not ohlcv_15m:
                    continue
                    
                df_15m = pd.DataFrame(ohlcv_15m, columns=["ts","open","high","low","close","volume"])
                df_15m["dt"] = df_15m["ts"].apply(ts_to_dt)
                df_15m.set_index("dt", inplace=True)

                signal_result = self._generate_15m_signal(df_15m, symbol, now)
                if signal_result:
                    # Add to signal pool for validation
                    sig = Signal(
                        symbol=symbol,
                        timeframe=config.timeframes.signal,
                        direction=signal_result["direction"],
                        strength=signal_result["strength"],
                        score=signal_result["score"],
                        created_at=now,
                        last_validated=now,
                        meta=signal_result,
                    )
                    self.pool.add(sig)
                    info.append(f"{symbol} -> {signal_result['direction']} {signal_result['strength']} skor={signal_result['score']:.2f}")
                    
            except Exception as e:
                info.append(f"{symbol} hata: {e}")
        
        # Validate signals in pool with 5m data
        await self._validate_signals_5m()
        
        self.last_status = " | ".join(info[-5:]) if info else "Tarama tamamlandı"

    def _generate_15m_signal(self, df: pd.DataFrame, symbol: str, timestamp: datetime):
        """Generate signal candidates on 15m timeframe as per specification"""
        if len(df) < 100:
            return None
            
        # Extract price data
        opens = df["open"]
        highs = df["high"]
        lows = df["low"]
        closes = df["close"]
        volumes = df["volume"]

        # Calculate indicators
        atr_values = atr(highs, lows, closes, config.indicators.atr_period)
        adx_val, di_plus, di_minus = adx(highs, lows, closes, config.indicators.adx_period)
        rsi_values = rsi(closes, config.indicators.rsi_period)
        volume_data = volume_analysis(volumes, config.indicators.volume_period)
        
        # SMC Analysis
        bos_choch = detect_bos_choch(df)
        fvg_data = detect_fvg(df)
        ob_data = detect_order_blocks(df)
        pd_zones = premium_discount_zones(df)
        
        # Price Action Analysis
        pa_analysis = analyze_price_action(df)
        
        # Current values (last candle)
        current_atr = float(atr_values.iloc[-1])
        current_adx = float(adx_val.iloc[-1])
        current_di_plus = float(di_plus.iloc[-1])
        current_di_minus = float(di_minus.iloc[-1])
        current_rsi = float(rsi_values.iloc[-1])
        current_close = float(closes.iloc[-1])
        current_volume_ratio = float(volume_data['volume_ratio'].iloc[-1])
        
        # Signal generation rules as per specification
        signal_conditions = self._check_signal_conditions(
            df, current_atr, current_adx, current_di_plus, current_di_minus,
            current_rsi, current_volume_ratio, bos_choch, fvg_data, ob_data, 
            pd_zones, pa_analysis
        )
        
        if not signal_conditions:
            return None
            
        direction = signal_conditions["direction"]
        entry = current_close
        
        # Calculate levels using new specification
        levels = atr_levels(
            entry, current_atr, direction, 
            config.risk.sl_atr_mult, 
            config.risk.tp_r_levels
        )
        
        # Check minimum R:R requirement
        if not meets_rr(entry, levels["sl"], levels["tp1"], config.risk.risk_reward_min):
            return None
        
        # Calculate signal score
        features = {
            "smc_strength": signal_conditions["smc_score"],
            "volume_strength": signal_conditions["volume_score"], 
            "trend_strength": signal_conditions["trend_score"],
            "momentum_strength": signal_conditions["momentum_score"],
        }
        
        score = score_signal(features)
        strength = strength_from_score(score)
        
        return {
            "direction": direction,
            "strength": strength,
            "score": score,
            "entry": entry,
            "atr": current_atr,
            "adx": current_adx,
            "di_plus": current_di_plus,
            "di_minus": current_di_minus,
            "volume_multiplier": current_volume_ratio,
            "structure_info": signal_conditions["structure_info"],
            "zone_info": signal_conditions["zone_info"],
            "momentum_status": signal_conditions["momentum_status"],
            **levels
        }
        
    def _check_signal_conditions(self, df, atr_val, adx_val, di_plus, di_minus, rsi_val, vol_ratio, bos_choch, fvg_data, ob_data, pd_zones, pa_analysis):
        """Check signal conditions as per specification"""
        
        # Minimum requirements
        if adx_val < config.indicators.adx_min:
            return None
        
        if atr_val <= 0:
            return None
            
        if vol_ratio < config.indicators.volume_multiplier_min:
            return None
        
        # Structure analysis (BOS/CHOCH confirmation)
        bos_signal = bos_choch['bos'].iloc[-1]
        choch_signal = bos_choch['choch'].iloc[-1]
        
        structure_confirmed = abs(bos_signal) > 0 or abs(choch_signal) > 0
        if not structure_confirmed:
            return None
            
        # Determine direction based on structure and trend
        if bos_signal > 0 or choch_signal > 0:  # Bullish structure
            direction = "long"
            trend_aligned = di_plus > di_minus
        else:  # Bearish structure
            direction = "short"
            trend_aligned = di_minus > di_plus
            
        if not trend_aligned:
            return None
        
        # Momentum alignment (not extremes)
        if direction == "long":
            momentum_ok = rsi_val >= config.indicators.rsi_min
        else:
            momentum_ok = rsi_val <= config.indicators.rsi_max
            
        if not momentum_ok:
            return None
        
        # Zone analysis (OB/FVG/premium-discount interaction)
        zone_info = "Unknown"
        zone_score = 0.3
        
        if direction == "long":
            if ob_data['ob_bullish'].iloc[-1]:
                zone_info = "Bullish OB"
                zone_score = 0.8
            elif fvg_data['fvg_bullish'].iloc[-1]:
                zone_info = "Bullish FVG"
                zone_score = 0.7
            elif pd_zones['discount'].iloc[-1]:
                zone_info = "Discount Zone"
                zone_score = 0.6
        else:
            if ob_data['ob_bearish'].iloc[-1]:
                zone_info = "Bearish OB"
                zone_score = 0.8
            elif fvg_data['fvg_bearish'].iloc[-1]:
                zone_info = "Bearish FVG"  
                zone_score = 0.7
            elif pd_zones['premium'].iloc[-1]:
                zone_info = "Premium Zone"
                zone_score = 0.6
        
        # Calculate component scores
        smc_score = 0.7 if structure_confirmed else 0.3
        volume_score = min(vol_ratio / config.indicators.volume_multiplier_min, 2.0) / 2.0
        trend_score = min(adx_val / config.indicators.adx_min, 2.0) / 2.0
        momentum_score = 0.7 if momentum_ok else 0.3
        
        structure_info = f"BOS={bos_signal:.0f}/CHOCH={choch_signal:.0f}"
        momentum_status = "uyumlu" if momentum_ok else "uyumsuz"
        
        return {
            "direction": direction,
            "smc_score": smc_score,
            "volume_score": volume_score,
            "trend_score": trend_score,
            "momentum_score": momentum_score,
            "structure_info": structure_info,
            "zone_info": zone_info,
            "momentum_status": momentum_status
        }

    async def _validate_signals_5m(self):
        """Validate signals using 5m timeframe as per specification"""
        validated_signals = []
        
        for signal in self.pool.get_pending_signals():
            try:
                # Fetch 5m data for validation
                ohlcv_5m = self.client.fetch_ohlcv(
                    signal.symbol, 
                    timeframe=config.timeframes.validation, 
                    limit=config.validation.candles_5m + 20  # Extra for analysis
                )
                
                if not ohlcv_5m:
                    continue
                    
                df_5m = pd.DataFrame(ohlcv_5m, columns=["ts","open","high","low","close","volume"])
                df_5m["dt"] = df_5m["ts"].apply(ts_to_dt)
                df_5m.set_index("dt", inplace=True)
                
                # Check validation criteria
                if self._validate_signal_5m(signal, df_5m):
                    validated_signals.append(signal)
                    
            except Exception as e:
                continue
        
        # Confirm validated signals and potentially create trades
        for signal in validated_signals:
            self.pool.confirm_signal(signal.symbol, signal.direction)
            
            # Create trade from confirmed signal
            self._create_trade_from_signal(signal)

    def _validate_signal_5m(self, signal: Signal, df_5m: pd.DataFrame) -> bool:
        """5m validation logic - 3 candles confirmation as per spec"""
        if len(df_5m) < config.validation.candles_5m:
            return False
            
        # Get last 3 candles for validation
        recent_candles = df_5m.tail(config.validation.candles_5m)
        
        # Price should maintain entry zone
        entry_price = signal.meta.get("entry", 0)
        price_range_tolerance = 0.02  # 2% tolerance
        
        for _, candle in recent_candles.iterrows():
            price_dev = abs(candle['close'] - entry_price) / entry_price
            if price_dev > price_range_tolerance:
                return False
        
        # Check for micro BOS (at least 1 as per spec)
        micro_bos_count = 0
        for i in range(1, len(recent_candles)):
            if signal.direction == "long":
                if recent_candles.iloc[i]['high'] > recent_candles.iloc[i-1]['high']:
                    micro_bos_count += 1
            else:
                if recent_candles.iloc[i]['low'] < recent_candles.iloc[i-1]['low']:
                    micro_bos_count += 1
        
        if micro_bos_count < config.validation.min_micro_bos:
            return False
        
        # Volume should not drop significantly unless allowed
        if not config.validation.allow_volume_drop:
            avg_volume = recent_candles['volume'].mean()
            signal_volume = signal.meta.get("volume_multiplier", 1.0)
            if avg_volume < signal_volume * 0.8:  # 20% drop tolerance
                return False
        
        return True

    def _create_trade_from_signal(self, signal: Signal):
        """Create a trade from confirmed signal"""
        trade_id = str(uuid.uuid4())[:8]
        
        direction = TradeDirection.LONG if signal.direction == "long" else TradeDirection.SHORT
        
        trade = Trade(
            id=trade_id,
            symbol=signal.symbol,
            direction=direction,
            entry_price=signal.meta["entry"],
            sl_price=signal.meta["sl"],
            tp1_price=signal.meta["tp1"],
            tp2_price=signal.meta["tp2"],
            tp3_price=signal.meta["tp3"],
            atr=signal.meta["atr"],
            adx=signal.meta["adx"],
            di_plus=signal.meta["di_plus"],
            di_minus=signal.meta["di_minus"],
            structure_info=signal.meta["structure_info"],
            zone_info=signal.meta["zone_info"],
            volume_multiplier=signal.meta["volume_multiplier"],
            momentum_status=signal.meta["momentum_status"],
            created_at=signal.created_at
        )
        
        self.tracker.add_trade(trade)
        return trade

    def get_confirmed_signals(self):
        """Get confirmed signals for Telegram notification"""
        return self.pool.get_confirmed_signals()
        
    def get_active_trades(self):
        """Get active trades for monitoring"""
        return self.tracker.get_active_trades()


async def run_engine():
    engine = Engine()
    while True:
        await engine.scan_once()
        await asyncio.sleep(30)  # 30s scan interval


if __name__ == "__main__":
    # CLI quick run: scanning only
    asyncio.run(run_engine())
