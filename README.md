# Crypto Funding Scanner

Real-time negative funding rate scanner for Binance Futures, Bybit Futures and Bitget Futures.

The project monitors USDT perpetual futures, finds the strongest negative funding rates, and displays the top results in a stable live console dashboard.

---

## Repository Description

Use this as the GitHub repository description:

```text
Real-time negative funding rate scanner for Binance, Bybit and Bitget perpetual futures.
```

---

## Features

- Binance Futures support
- Bybit Futures support
- Bitget Futures support
- USDT perpetual futures only
- Top negative funding rates per exchange
- Funding countdown timer
- 24h volume display
- Stable fixed-width console table
- Smooth console rendering without constant `cls`
- Windows BAT launcher
- Automatic Python version check
- Automatic virtual environment creation
- Automatic dependency installation
- Public APIs only
- No API keys required
- No trading functions
- English-only interface

---

## Console Output

The scanner displays:

| Column | Description |
|---|---|
| # | Ranking number |
| Symbol | Futures symbol |
| Funding % | Current funding rate |
| Time Left | Countdown until next funding |
| Volume 24h | 24-hour volume |

The scanner does **not** display:

- current asset price
- Edge column
- Next Funding date/time

---

## How It Works

1. The scanner requests public market data from Binance, Bybit and Bitget.
2. It filters only USDT perpetual futures.
3. It keeps only symbols with negative funding rates.
4. It sorts symbols from the most negative funding rate to less negative.
5. It displays the top results per exchange.
6. Market data refreshes every `REFRESH_SEC`.
7. `Time Left` updates every second.

---

## Project Structure

```text
crypto-funding-scanner/
│
├── exchanges/
│   ├── __init__.py
│   ├── binance.py
│   ├── bybit.py
│   └── bitget.py
│
├── main.py
├── utils.py
├── requirements.txt
├── run_scanner.bat
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── TECHNICAL_SPECIFICATION_EN.md
└── GITHUB_PUBLISH_GUIDE.md
```

---

## Requirements

- Windows 10/11
- Python 3.10+
- Internet connection

Python packages:

```text
requests
python-dotenv
```

---

## Quick Start on Windows

1. Download or clone the repository.
2. Open the project folder.
3. Run:

```bat
run_scanner.bat
```

The BAT launcher will:

1. Check installed Python versions.
2. Use Python 3.10+ if available.
3. Try to install Python 3.12 via `winget` if no compatible Python is found.
4. Create `venv`.
5. Install dependencies from `requirements.txt`.
6. Create `.env` from `.env.example` if missing.
7. Start the scanner.

---

## Manual Start

```bash
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
venv\Scripts\python.exe main.py
```

---

## Environment Variables

`.env.example`:

```env
REFRESH_SEC=5
TOP_N=3
QUOTE=USDT
MIN_VOLUME_24H_USDT=0
HTTP_TIMEOUT_SEC=10
HTTP_RETRIES=2
```

### Settings

| Variable | Default | Description |
|---|---:|---|
| `REFRESH_SEC` | `5` | Market data refresh interval |
| `TOP_N` | `3` | Number of symbols shown per exchange |
| `QUOTE` | `USDT` | Quote currency filter |
| `MIN_VOLUME_24H_USDT` | `0` | Minimum 24h volume filter |
| `HTTP_TIMEOUT_SEC` | `10` | HTTP request timeout |
| `HTTP_RETRIES` | `2` | API request retry count |

---

## Stable Console Rendering

The dashboard is rendered as one complete frame.

This avoids:

- constant screen clearing
- visible ANSI escape codes
- console scroll drift
- broken redraw in Windows CMD

Market data refreshes every `REFRESH_SEC`.
The funding countdown updates every second.

---

## Safety

This project is a scanner only.

It does not:

- place orders
- trade automatically
- require API keys
- access private account data
- manage funds

All exchange data is retrieved from public market endpoints.

---

## Disclaimer

This tool is for informational and educational purposes only. It is not financial advice. Funding rates, futures markets and crypto assets are volatile. Use your own risk management and verify all data before making trading decisions.

---

## License

MIT License.
