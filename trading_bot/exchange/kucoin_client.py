import ccxt
from typing import List, Dict
import numpy as np
import time


class KucoinClient:
    def __init__(self):
        try:
            self.client = ccxt.kucoin()
            self.client.load_markets()
            self.offline_mode = False
        except Exception:
            # Fallback to offline mode for testing
            self.client = None
            self.offline_mode = True
            print("⚠️  KuCoin API not available, running in offline mode with simulated data")

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> List[List[float]]:
        if self.offline_mode:
            return self._generate_fake_ohlcv(symbol, limit)
        
        try:
            return self.client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        except Exception as e:
            print(f"⚠️  API error for {symbol}, using simulated data: {e}")
            return self._generate_fake_ohlcv(symbol, limit)

    def _generate_fake_ohlcv(self, symbol: str, limit: int) -> List[List[float]]:
        """Generate realistic fake OHLCV data for testing"""
        # Base prices for different symbols
        base_prices = {
            "BTC/USDT": 60000,
            "ETH/USDT": 4000, 
            "SOL/USDT": 140,
            "BNB/USDT": 600,
            "XRP/USDT": 0.5,
            "DOGE/USDT": 0.08
        }
        
        base_price = base_prices.get(symbol, 100)
        current_time = int(time.time() * 1000)
        
        # Generate realistic price movement
        ohlcv_data = []
        current_price = base_price
        
        for i in range(limit):
            # Random walk with slight trending
            change_pct = np.random.normal(0, 0.02)  # 2% volatility
            current_price = current_price * (1 + change_pct)
            
            # Generate OHLC from current price
            volatility = abs(change_pct) * 0.5
            high = current_price * (1 + volatility)
            low = current_price * (1 - volatility)
            open_price = current_price * (1 + np.random.normal(0, 0.005))
            close_price = current_price
            
            # Volume (higher volume with bigger moves)
            volume = np.random.uniform(1000, 10000) * (1 + abs(change_pct) * 10)
            
            timestamp = current_time - (limit - i) * 900000  # 15m intervals
            
            ohlcv_data.append([
                timestamp,
                float(open_price),
                float(high),
                float(low), 
                float(close_price),
                float(volume)
            ])
            
        return ohlcv_data

    def market_symbols(self) -> List[str]:
        if self.offline_mode:
            return ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "DOGE/USDT"]
        return list(self.client.symbols)

    def price_precision(self, symbol: str) -> int:
        if self.offline_mode:
            return 6
        market = self.client.market(symbol)
        return market.get("precision", {}).get("price", 6)

    def amount_precision(self, symbol: str) -> int:
        if self.offline_mode:
            return 6
        market = self.client.market(symbol)
        return market.get("precision", {}).get("amount", 6)

