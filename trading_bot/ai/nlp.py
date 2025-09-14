import re
from typing import Dict, Any, List, Tuple

from trading_bot.config import config


def _set_param(path: List[str], value: Any) -> Tuple[bool, str]:
    target = config
    for key in path[:-1]:
        target = getattr(target, key)
    attr = path[-1]
    if not hasattr(target, attr):
        return False, f"Parametre bulunamadı: {'.'.join(path)}"
    try:
        current = getattr(target, attr)
        if isinstance(current, int):
            value = int(value)
        elif isinstance(current, float):
            value = float(value)
        elif isinstance(current, list):
            if isinstance(value, str):
                value = [v.strip() for v in value.split(',') if v.strip()]
        setattr(target, attr, value)
        return True, f"{'.'.join(path)} = {value}"
    except Exception as e:
        return False, str(e)


def handle_text_command(text: str) -> str:
    t = text.strip().lower()
    # RSI periyodunu 14 yap
    m = re.search(r"rsi\s*periyodunu\s*(\d+)\s*yap", t)
    if m:
        ok, msg = _set_param(["indicators", "rsi_period"], int(m.group(1)))
        return msg

    # Stop loss oranını %2'ye çıkar -> interpret as atr_multiplier approx 2.0
    m = re.search(r"stop\s*loss\s*oranını\s*%?(\d+(?:[\.,]\d+)?)['’]?ye\s*çık(ar)?", t)
    if m:
        val = float(m.group(1).replace(',', '.')) / 100.0
        # Map to risk_per_trade for simplicity
        ok, msg = _set_param(["risk", "risk_per_trade"], val)
        return msg

    # Sadece 4H ve 1H trend aynı yönde olan sinyalleri al -> not fully supported, acknowledge filter flag
    if "trend aynı yönde" in t:
        return "Trend uyum filtresi şu an kısmen destekleniyor (EMA hizası)."

    # Havuzdaki tüm bekleyen sinyalleri göster -> handled by /havuz
    if "havuz" in t and "bekleyen" in t:
        return "Havuz için /havuz komutunu kullanın."

    # PEPE ve DOGE coinlerini takipten çıkar
    m = re.search(r"(.*?)\s*coinlerini\s*takipten\s*çıkar", t)
    if m:
        coins = [c.strip().upper() for c in re.split(r"[,\s]+ve[,\s]+|,|\s+", m.group(1)) if c.strip()]
        before = list(config.symbols.tickers)
        after = [s for s in before if all(c not in s.upper() for c in coins)]
        config.symbols.tickers = after
        removed = [s for s in before if s not in after]
        return f"Kaldırıldı: {', '.join(removed)}" if removed else "Eşleşen sembol bulunamadı."

    # RSI periyodunu 14 yap ve sadece güçlü sinyalleri işle
    if "sadece güçlü sinyalleri işle" in t:
        return "Güç filtresi notu: STRONG sinyallere öncelik verilecek (bilgi)."

    # Sadece volume breakout olan sinyalleri işle -> acknowledge
    if "volume breakout" in t:
        return "Hacim anomali filtresi şimdilik bilgilendirici; sinyal puanına yansıyor."

    # Son 24 saatteki en başarılı coinleri listele -> not implemented
    if "en başarılı coinleri listele" in t:
        return "İstatistik modülü sınırlı; yakında daha detaylı rapor."

    return "Komut anlaşılamadı veya henüz desteklenmiyor."
