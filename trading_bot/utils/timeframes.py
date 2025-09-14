from datetime import datetime
from dateutil import tz


def ts_to_dt(ts_ms: int) -> datetime:
    return datetime.fromtimestamp(ts_ms / 1000, tz=tz.UTC)


def timeframe_to_minutes(tf: str) -> int:
    tf = tf.lower()
    if tf.endswith("m"):
        return int(tf[:-1])
    if tf.endswith("h"):
        return int(tf[:-1]) * 60
    if tf.endswith("d"):
        return int(tf[:-1]) * 60 * 24
    raise ValueError(f"Unsupported timeframe: {tf}")
