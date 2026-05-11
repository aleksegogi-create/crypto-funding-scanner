from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import requests


@dataclass
class FundingItem:
    exchange: str
    symbol: str
    funding_rate: float
    next_funding_ms: Optional[int]
    volume_24h_usdt: Optional[float] = None
    edge_pct: Optional[float] = None


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default


def http_get_json(url: str, params: Optional[dict[str, Any]] = None, timeout: float = 10, retries: int = 2) -> Any:
    last_error: Optional[Exception] = None
    headers = {"User-Agent": "crypto-funding-scanner/1.0"}

    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.35 * (attempt + 1))

    raise RuntimeError(f"GET failed: {url} params={params} error={last_error}")


def countdown_from_ms(ms: Optional[int]) -> str:
    if not ms:
        return "n/a"

    left = int(ms / 1000 - datetime.now(timezone.utc).timestamp())
    if left < 0:
        left = 0

    hours = left // 3600
    minutes = (left % 3600) // 60
    seconds = left % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def fmt_pct_decimal(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.4f}%"


def fmt_volume(value: Optional[float]) -> str:
    if value is None:
        return "n/a"

    abs_value = abs(value)

    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.2f}K"

    return f"{value:.2f}"


def normalize_symbol(symbol: str) -> str:
    return symbol.replace("_UMCBL", "").replace("-USDT", "USDT").upper()


def compute_edge_pct(funding_rate_decimal: float) -> float:
    return abs(funding_rate_decimal) * 100.0


def table_lines(exchange_name: str, rows: list[FundingItem], error: Optional[str] = None) -> list[str]:
    lines: list[str] = []
    lines.append("")
    lines.append(exchange_name)

    if error:
        lines.append(f"ERROR: {error}")
        return lines

    if not rows:
        lines.append("No negative funding found for current filters.")
        return lines

    separator = "+----+--------------------+--------------+------------+--------------+"
    lines.append(separator)
    lines.append(f"| {'#':<2} | {'Symbol':<18} | {'Funding %':>12} | {'Time Left':>10} | {'Volume 24h':>12} |")
    lines.append(separator)

    for index, item in enumerate(rows, 1):
        lines.append(
            f"| {index:<2} | "
            f"{item.symbol:<18} | "
            f"{fmt_pct_decimal(item.funding_rate):>12} | "
            f"{countdown_from_ms(item.next_funding_ms):>10} | "
            f"{fmt_volume(item.volume_24h_usdt):>12} |"
        )

    lines.append(separator)
    return lines


class StableConsole:
    """
    Stable Windows console renderer.

    It avoids:
    - repeated cls calls
    - ANSI cursor sequences printed as text
    - scrollback growth during redraw

    The dashboard is built as one complete frame and written from the top-left.
    """

    def __init__(self) -> None:
        self._is_windows = os.name == "nt"
        self._last_height = 0
        self._initialized = False
        self._kernel32 = None
        self._handle = None

        if self._is_windows:
            try:
                import ctypes

                self._ctypes = ctypes
                self._kernel32 = ctypes.windll.kernel32
                self._handle = self._kernel32.GetStdHandle(-11)
            except Exception:
                self._kernel32 = None
                self._handle = None

    def initialize(self) -> None:
        if self._initialized:
            return

        os.system("cls" if self._is_windows else "clear")
        self._hide_cursor()
        self._initialized = True

    def close(self) -> None:
        self._show_cursor()
        sys.stdout.write("\n")
        sys.stdout.flush()

    def draw(self, frame: str) -> None:
        self.initialize()

        lines = frame.splitlines()
        frame_height = len(lines)

        if self._is_windows and self._kernel32 and self._handle:
            self._windows_home()
            sys.stdout.write(frame)

            # Clear leftovers from previous longer frame without scrolling.
            extra = max(0, self._last_height - frame_height)
            if extra:
                sys.stdout.write("\n" * extra)

            sys.stdout.flush()
        else:
            # Non-Windows fallback.
            sys.stdout.write("\033[H")
            sys.stdout.write(frame)
            extra = max(0, self._last_height - frame_height)
            if extra:
                sys.stdout.write("\n" * extra)
            sys.stdout.flush()

        self._last_height = frame_height

    def _windows_home(self) -> None:
        try:
            ctypes = self._ctypes

            class COORD(ctypes.Structure):
                _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

            self._kernel32.SetConsoleCursorPosition(self._handle, COORD(0, 0))
        except Exception:
            pass

    def _hide_cursor(self) -> None:
        if not (self._is_windows and self._kernel32 and self._handle):
            return

        try:
            ctypes = self._ctypes

            class CONSOLE_CURSOR_INFO(ctypes.Structure):
                _fields_ = [("dwSize", ctypes.c_uint32), ("bVisible", ctypes.c_int)]

            info = CONSOLE_CURSOR_INFO()
            info.dwSize = 25
            info.bVisible = 0
            self._kernel32.SetConsoleCursorInfo(self._handle, ctypes.byref(info))
        except Exception:
            pass

    def _show_cursor(self) -> None:
        if not (self._is_windows and self._kernel32 and self._handle):
            return

        try:
            ctypes = self._ctypes

            class CONSOLE_CURSOR_INFO(ctypes.Structure):
                _fields_ = [("dwSize", ctypes.c_uint32), ("bVisible", ctypes.c_int)]

            info = CONSOLE_CURSOR_INFO()
            info.dwSize = 25
            info.bVisible = 1
            self._kernel32.SetConsoleCursorInfo(self._handle, ctypes.byref(info))
        except Exception:
            pass
