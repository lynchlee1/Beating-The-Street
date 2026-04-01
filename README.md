# Beating The Street — Financial Report Generation Tool

Generates fully offline, single-file interactive HTML financial dashboards from a ticker symbol.
Built with a modern **React + Recharts** frontend and a modular **Python** data pipeline.

## Key Features

- **In-depth Financial Analysis** — Valuation, Operations, Financial Stability, Capital Structure.
- **Long-Term Trend Analysis** — 3 / 5 / 10 / 13 / 20 year averages for all major indicators.
- **Interactive React Dashboard** — Switch between Quarterly, Trailing 1Y and Trailing 3Y views.
- **Custom Chart Builder** — Select and combine any metrics to create your own charts on the fly.
- **Offline Static HTML** — Download a fully self-contained HTML file that works without internet.
- **Extensible Architecture** — Swap out data providers by implementing `BaseFinancialClient`.

## Project Structure

```
Beating-The-Street/
├── .env                  # API key (never committed – copy from .env.example)
├── .env.example          # Template for .env
├── requirements.txt      # Python dependencies
├── run.py                # Main entry point
└── src/
    ├── fetcher/          # (1) API → raw financial data
    │   ├── base_client.py    # Abstract interface for any data provider
    │   └── fmp_client.py     # Financial Modeling Prep implementation
    ├── parser/           # (2) Raw data → calculated metrics JSON
    │   └── calculator.py     # Trailing series, averages, growth, valuation
    ├── builder/          # (3) JSON + React template → offline HTML
    │   └── html_injector.py
    └── ui/               # React frontend (Vite + Recharts)
        ├── package.json
        ├── vite.config.js    # vite-plugin-singlefile for offline HTML
        └── src/
            ├── App.jsx
            └── components/
```

## Quick Start

### 1. Configure your API key

```bash
cp .env.example .env
# Edit .env and set FMP_API_KEY=your_key_here
```

Get a free API key at [financialmodelingprep.com](https://financialmodelingprep.com).

### 2. Install dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node/React dependencies (first time only)
cd src/ui && npm install && cd ../..
```

### 3. Build the React app (first time only)

```bash
cd src/ui && npm run build && cd ../..
```

### 4. Generate a report

```bash
# Single ticker
python run.py AAPL

# Multiple tickers
python run.py AAPL MSFT GOOG

# Skip rebuilding React (faster after first build)
python run.py AAPL --skip-build
```

Reports are saved to `reports/report_<TICKER>_<timestamp>.html`.
Open any report in a browser — no internet connection required.

### UI Development

To develop and preview the React UI with live reload and mock data:

```bash
cd src/ui && npm run dev
# Open http://localhost:5173
```

## Adding a New Data Provider

1. Create a new file in `src/fetcher/`, e.g. `src/fetcher/my_provider.py`.
2. Subclass `BaseFinancialClient` and implement all abstract methods.
3. Pass an instance of your new client to the pipeline in `run.py`.
