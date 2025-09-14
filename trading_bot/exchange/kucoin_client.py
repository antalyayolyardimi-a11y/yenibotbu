import ccxt
from typing import List, Dict


class KucoinClient:
    def __init__(self):
        self.client = ccxt.kucoin()
        self.client.load_markets()

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> List[List[float]]:
        return self.client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def market_symbols(self) -> List[str]:
        return list(self.client.symbols)

    def price_precision(self, symbol: str) -> int:
        market = self.client.market(symbol)
        return market.get("precision", {}).get("price", 6)

    def amount_precision(self, symbol: str) -> int:
        market = self.client.market(symbol)
        return market.get("precision", {}).get("amount", 6)

