#!/usr/bin/env python3
"""Main entry point for Beating-The-Street financial report generation.

Usage
-----
    python run.py AAPL
    python run.py AAPL MSFT GOOG          # multiple tickers
    python run.py AAPL --output my_report.html
    python run.py AAPL --skip-build        # skip React npm build step

Pipeline
--------
  1. Fetch  : FMPClient  → raw financial data
  2. Parse  : calculator → UI-ready JSON
  3. Build  : html_injector → offline static HTML
"""

import argparse
import subprocess
import sys
from pathlib import Path
import time

# ── make sure src/ is importable ──────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.fetcher import FMPClient
from src.parser import build_parsed_data
from src.parser.calculator import InsufficientDataError
from src.builder import generate_static_html


UI_DIR = ROOT / "src" / "ui"


def build_react_app() -> bool:
    """Run `npm run build` in src/ui/.  Returns True on success."""
    if not (UI_DIR / "package.json").exists():
        print("⚠  src/ui/package.json not found – skipping React build.")
        return False

    print("🔨  Building React app…")
    node_modules = UI_DIR / "node_modules"
    if not node_modules.exists():
        print("   Installing npm dependencies…")
        result = subprocess.run(
            ["npm", "install"],
            cwd=UI_DIR,
            capture_output=False,
        )
        if result.returncode != 0:
            print("❌  npm install failed.")
            return False

    result = subprocess.run(["npm", "run", "build"], cwd=UI_DIR, capture_output=False)
    if result.returncode != 0:
        print("❌  npm run build failed.")
        return False

    print("✅  React app built successfully.")
    return True


def process_ticker(client: FMPClient, ticker: str, output: Path | None) -> bool:
    """Fetch → Parse → Build for a single ticker.  Returns True on success."""
    print(f"\n{'─'*60}")
    print(f"  Processing: {ticker}")
    print(f"{'─'*60}")

    # 1. Fetch
    print("  [1/3] Fetching data…")
    try:
        raw = client.fetch_all(ticker)
    except Exception as exc:
        print(f"  ❌  Fetch failed: {exc}")
        return False

    if isinstance(raw, list):
        # Error sentinel returned from fetch_all
        print(f"  ⚠  Skipping {ticker}: {raw}")
        return False

    # 2. Parse
    print("  [2/3] Parsing & calculating metrics…")
    try:
        parsed = build_parsed_data(raw)
    except InsufficientDataError as exc:
        print(f"  ⚠  Skipping {ticker}: {exc}")
        return False
    except Exception as exc:
        print(f"  ❌  Parse failed: {exc}")
        return False

    # 3. Build
    print("  [3/3] Generating offline HTML…")
    if output is None:
        ts = int(time.time())
        out_path = ROOT / "reports" / f"report_{ticker}_{ts}.html"
    else:
        out_path = output

    try:
        generate_static_html(parsed, output_path=out_path)
    except FileNotFoundError as exc:
        print(f"  ❌  {exc}")
        return False
    except Exception as exc:
        print(f"  ❌  Build failed: {exc}")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate offline financial report HTML files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "tickers",
        nargs="+",
        metavar="TICKER",
        help="One or more stock tickers (e.g. AAPL MSFT)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Custom output file path (only valid with a single ticker).",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        default=False,
        help="Skip the `npm run build` step (use existing dist/).",
    )
    args = parser.parse_args()

    if args.output and len(args.tickers) > 1:
        parser.error("--output can only be used with a single ticker.")

    # Build React app unless told to skip
    if not args.skip_build:
        build_react_app()

    client = FMPClient()
    successes, failures = [], []

    for ticker in args.tickers:
        ok = process_ticker(client, ticker.upper(), args.output)
        (successes if ok else failures).append(ticker.upper())

    print(f"\n{'═'*60}")
    print(f"  Done.  {len(successes)} succeeded, {len(failures)} failed.")
    if failures:
        print(f"  Failed tickers: {', '.join(failures)}")
    print(f"{'═'*60}\n")

    sys.exit(0 if not failures else 1)


if __name__ == "__main__":
    main()
