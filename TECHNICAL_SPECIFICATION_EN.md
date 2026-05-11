# TECHNICAL SPECIFICATION — CRYPTO FUNDING SCANNER

## Purpose

Build a lightweight real-time crypto funding scanner for perpetual futures exchanges.

The application must continuously monitor negative funding rates and display the strongest opportunities in a live console dashboard.

---

# Exchanges

Supported exchanges:
- Binance Futures
- Bybit Futures
- Bitget Futures

Only USDT perpetual futures pairs are supported.

---

# Functional Requirements

The scanner must:
- retrieve funding rates from public APIs
- filter only negative funding rates
- sort results from most negative to least negative
- display top N symbols per exchange
- continuously update countdown timers
- refresh market data automatically

---

# Console Requirements

The console dashboard must:
- use fixed-width aligned tables
- avoid console scrolling
- avoid visible ANSI escape sequences
- avoid repeated `cls`
- redraw in-place smoothly
- support standard Windows CMD

---

# Data Display

The dashboard must display:
- Symbol
- Funding %
- Time Left
- Volume 24h

The dashboard must NOT display:
- current price
- edge column
- next funding timestamp

---

# Timing Logic

Two independent update cycles are required:

1. Market data refresh:
   - configurable through `REFRESH_SEC`
   - default: 5 seconds

2. Countdown refresh:
   - updates every second
   - independent from API refresh cycle

---

# Environment Variables

Required `.env` settings:

```env
REFRESH_SEC=5
TOP_N=3
QUOTE=USDT
MIN_VOLUME_24H_USDT=0
HTTP_TIMEOUT_SEC=10
HTTP_RETRIES=2
```

---

# Launcher Requirements

`run_scanner.bat` must:
- detect installed Python versions
- support Python 3.10–3.13
- create virtual environment automatically
- install dependencies automatically
- recreate broken venv automatically
- launch scanner automatically

If compatible Python is missing:
- attempt Python 3.12 installation through winget
- continue launcher flow after installation

---

# Stability Requirements

The scanner must:
- continue running if one exchange fails
- handle request timeouts
- avoid crashing from malformed responses
- handle temporary API failures gracefully

---

# Project Status

Current project state:
STABLE BASELINE
