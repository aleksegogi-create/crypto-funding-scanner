from __future__ import annotations

from typing import Optional

from utils import FundingItem, compute_edge_pct, http_get_json

BASE_URL = "https://fapi.binance.com"


def fetch_top_negative(top_n: int, quote: str, min_volume_24h_usdt: float, timeout: float, retries: int) -> list[FundingItem]:
    # /fapi/v1/premiumIndex returns mark price, lastFundingRate and nextFundingTime.
    premium = http_get_json(f"{BASE_URL}/fapi/v1/premiumIndex", timeout=timeout, retries=retries)
    tickers = http_get_json(f"{BASE_URL}/fapi/v1/ticker/24hr", timeout=timeout, retries=retries)

    volumes: dict[str, Optional[float]] = {}
    for t in tickers:
        symbol = str(t.get("symbol", ""))
        try:
            volumes[symbol] = float(t.get("quoteVolume", 0.0))
        except Exception:
            volumes[symbol] = None

    rows: list[FundingItem] = []
    for p in premium:
        symbol = str(p.get("symbol", ""))
        if not symbol.endswith(quote):
            continue
        try:
            rate = float(p.get("lastFundingRate"))
        except Exception:
            continue
        if rate >= 0:
            continue
        volume = volumes.get(symbol)
        if volume is not None and volume < min_volume_24h_usdt:
            continue
        try:
            next_ms = int(p.get("nextFundingTime"))
        except Exception:
            next_ms = None
        rows.append(
            FundingItem(
                exchange="BINANCE FUTURES",
                symbol=symbol,
                funding_rate=rate,
                next_funding_ms=next_ms,
                volume_24h_usdt=volume,
                edge_pct=compute_edge_pct(rate),
            )
        )

    rows.sort(key=lambda x: x.funding_rate)
    return rows[:top_n]
