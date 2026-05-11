from __future__ import annotations

import os
import time

from dotenv import load_dotenv

from exchanges import binance, bitget, bybit
from utils import StableConsole, env_float, env_int, table_lines


def safe_fetch(name: str, fn, top_n: int, quote: str, min_volume: float, timeout: float, retries: int):
    try:
        return fn(top_n, quote, min_volume, timeout, retries), None
    except Exception as exc:
        return [], str(exc)


def fetch_all(top_n: int, quote: str, min_volume: float, timeout: float, retries: int):
    return {
        "BINANCE FUTURES": safe_fetch("BINANCE", binance.fetch_top_negative, top_n, quote, min_volume, timeout, retries),
        "BYBIT FUTURES": safe_fetch("BYBIT", bybit.fetch_top_negative, top_n, quote, min_volume, timeout, retries),
        "BITGET FUTURES": safe_fetch("BITGET", bitget.fetch_top_negative, top_n, quote, min_volume, timeout, retries),
    }


def build_dashboard_frame(results, top_n: int, quote: str, min_volume: float, refresh_sec: int) -> str:
    lines: list[str] = []

    lines.append("=" * 86)
    lines.append("CRYPTO FUNDING SCANNER | Binance / Bybit / Bitget")
    lines.append(f"TOP_N={top_n} | QUOTE={quote} | MIN_VOLUME_24H_USDT={min_volume:g} | REFRESH_SEC={refresh_sec}")
    lines.append("=" * 86)
    lines.append("USDT perpetual futures only. Negative funding rates only.")
    lines.append("No trading functions. Public market data only.")

    for exchange_name, (rows, error) in results.items():
        lines.extend(table_lines(exchange_name, rows, error=error))

    lines.append("")
    lines.append("Press Ctrl+C to stop.")
    lines.append("Market data refreshes every REFRESH_SEC. Time Left updates every second.")

    # Extra empty lines overwrite any leftovers if the frame becomes shorter.
    lines.extend([""] * 6)

    return "\n".join(lines)


def main() -> None:
    load_dotenv()

    refresh_sec = max(1, env_int("REFRESH_SEC", 5))
    top_n = max(1, env_int("TOP_N", 3))
    quote = "".join(ch for ch in os.getenv("QUOTE", "USDT").upper() if ch.isalnum()) or "USDT"
    min_volume = env_float("MIN_VOLUME_24H_USDT", 0.0)
    timeout = env_float("HTTP_TIMEOUT_SEC", 10.0)
    retries = env_int("HTTP_RETRIES", 2)

    console = StableConsole()

    results = fetch_all(top_n, quote, min_volume, timeout, retries)
    last_fetch_ts = time.monotonic()

    try:
        while True:
            now = time.monotonic()

            if now - last_fetch_ts >= refresh_sec:
                results = fetch_all(top_n, quote, min_volume, timeout, retries)
                last_fetch_ts = now

            frame = build_dashboard_frame(results, top_n, quote, min_volume, refresh_sec)
            console.draw(frame)

            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        console.close()
        print("Scanner stopped.")


if __name__ == "__main__":
    main()
