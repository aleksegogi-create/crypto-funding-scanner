from __future__ import annotations

import concurrent.futures
from typing import Any, Optional

from utils import FundingItem, compute_edge_pct, http_get_json, normalize_symbol

BASE_URL = "https://api.bitget.com"
PRODUCT_TYPE = "usdt-futures"


def _get_tickers(timeout: float, retries: int) -> list[dict[str, Any]]:
    data = http_get_json(
        f"{BASE_URL}/api/v2/mix/market/tickers",
        params={"productType": PRODUCT_TYPE},
        timeout=timeout,
        retries=retries,
    )
    if str(data.get("code")) != "00000":
        raise RuntimeError(f"Bitget code={data.get('code')} msg={data.get('msg')}")
    return data.get("data", []) or []


def _get_next_funding_ms(symbol: str, timeout: float, retries: int) -> Optional[int]:
    data = http_get_json(
        f"{BASE_URL}/api/v2/mix/market/funding-time",
        params={"symbol": symbol, "productType": PRODUCT_TYPE},
        timeout=timeout,
        retries=retries,
    )
    if str(data.get("code")) != "00000":
        return None
    payload = data.get("data")
    if isinstance(payload, list) and payload:
        payload = payload[0]
    if not isinstance(payload, dict):
        return None
    for key in ("nextFundingTime", "fundingTime", "nextSettleTime"):
        val = payload.get(key)
        if val is not None:
            try:
                return int(val)
            except Exception:
                pass
    return None


def fetch_top_negative(top_n: int, quote: str, min_volume_24h_usdt: float, timeout: float, retries: int) -> list[FundingItem]:
    tickers = _get_tickers(timeout, retries)
    candidates: list[FundingItem] = []

    for t in tickers:
        raw_symbol = str(t.get("symbol", ""))
        symbol = normalize_symbol(raw_symbol)
        if not symbol.endswith(quote):
            continue

        rate_raw = t.get("fundingRate") or t.get("funding_rate")
        try:
            rate = float(rate_raw)
        except Exception:
            continue
        if rate >= 0:
            continue

        volume = None
        for key in ("quoteVolume", "usdtVolume", "turnover24h", "quoteVolume24h"):
            if t.get(key) is not None:
                try:
                    volume = float(t.get(key))
                    break
                except Exception:
                    pass
        # Fallback: base volume * last price.
        if volume is None:
            try:
                base_vol = float(t.get("baseVolume") or t.get("volume24h") or 0.0)
                last = float(t.get("lastPr") or t.get("last") or t.get("lastPrice") or 0.0)
                volume = base_vol * last if base_vol and last else None
            except Exception:
                volume = None

        if volume is not None and volume < min_volume_24h_usdt:
            continue

        candidates.append(
            FundingItem(
                exchange="BITGET FUTURES",
                symbol=symbol,
                funding_rate=rate,
                next_funding_ms=None,
                volume_24h_usdt=volume,
                edge_pct=compute_edge_pct(rate),
            )
        )

    candidates.sort(key=lambda x: x.funding_rate)
    top = candidates[:top_n]

    # Bitget next funding time is requested by symbol. Do it only for top-N to avoid heavy API load.
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(max(top_n, 1), 5)) as executor:
        futures = {
            executor.submit(_get_next_funding_ms, item.symbol, timeout, retries): item
            for item in top
        }
        for fut in concurrent.futures.as_completed(futures):
            item = futures[fut]
            try:
                item.next_funding_ms = fut.result()
            except Exception:
                item.next_funding_ms = None

    return top
