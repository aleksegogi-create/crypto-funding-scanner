from __future__ import annotations

from typing import Optional

from utils import FundingItem, compute_edge_pct, http_get_json

BASE_URL = "https://api.bybit.com"


def fetch_top_negative(top_n: int, quote: str, min_volume_24h_usdt: float, timeout: float, retries: int) -> list[FundingItem]:
    data = http_get_json(
        f"{BASE_URL}/v5/market/tickers",
        params={"category": "linear"},
        timeout=timeout,
        retries=retries,
    )
    if str(data.get("retCode")) != "0":
        raise RuntimeError(f"Bybit retCode={data.get('retCode')} retMsg={data.get('retMsg')}")

    tickers = data.get("result", {}).get("list", [])
    rows: list[FundingItem] = []
    for t in tickers:
        symbol = str(t.get("symbol", ""))
        if not symbol.endswith(quote):
            continue
        try:
            rate = float(t.get("fundingRate"))
        except Exception:
            continue
        if rate >= 0:
            continue

        volume = None
        try:
            # turnover24h is quote turnover, usually USDT for linear USDT contracts.
            volume = float(t.get("turnover24h", 0.0))
        except Exception:
            pass
        if volume is not None and volume < min_volume_24h_usdt:
            continue

        try:
            next_ms = int(t.get("nextFundingTime"))
        except Exception:
            next_ms = None

        rows.append(
            FundingItem(
                exchange="BYBIT FUTURES",
                symbol=symbol,
                funding_rate=rate,
                next_funding_ms=next_ms,
                volume_24h_usdt=volume,
                edge_pct=compute_edge_pct(rate),
            )
        )

    rows.sort(key=lambda x: x.funding_rate)
    return rows[:top_n]
