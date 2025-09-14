import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


class JsonStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"trades": [], "stats": {}})

    def _read(self) -> Dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: Dict[str, Any]):
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        tmp.replace(self.path)

    def add_trade(self, trade: Dict[str, Any]):
        data = self._read()
        data.setdefault("trades", []).append(trade)
        self._write(data)

    def list_trades(self) -> List[Dict[str, Any]]:
        return self._read().get("trades", [])

    def update_stats(self, stats: Dict[str, Any]):
        data = self._read()
        data["stats"] = stats
        self._write(data)

    def get_stats(self) -> Dict[str, Any]:
        return self._read().get("stats", {})
