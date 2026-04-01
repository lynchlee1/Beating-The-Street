#!/usr/bin/env python3
"""Generate a virtual demo report from sample data without requiring an API key.

This script is the primary entry point for testing the full pipeline
(parse → build) without any network connectivity or FMP API key.

Usage
-----
    python tests/generate_demo_report.py
    python tests/generate_demo_report.py --output /tmp/demo.html
    python tests/generate_demo_report.py --ticker ACME --quarters 80

The generated HTML is completely self-contained and works offline in any browser.
"""

import argparse
import sys
import time
from pathlib import Path

# Make the repo root importable regardless of where the script is called from.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tests.fixtures.sample_raw import build_sample_raw
from src.parser import build_parsed_data
from src.builder import generate_static_html


TEMPLATE_PATH = REPO_ROOT / "src" / "ui" / "dist" / "index.html"


def generate_demo(
    ticker: str = "DEMO",
    n_quarters: int = 80,
    output: Path | None = None,
) -> Path:
    """Run the parse → build pipeline on synthetic sample data.

    Parameters
    ----------
    ticker:
        Ticker symbol displayed in the dashboard.
    n_quarters:
        Number of quarters of sample data to generate (min 52 required).
    output:
        Destination HTML path.  Defaults to ``reports/demo_<ticker>_<ts>.html``.

    Returns
    -------
    Path
        Absolute path to the generated HTML file.
    """
    print(f"📊  Building DEMO report for '{ticker}' ({n_quarters} quarters of sample data)…")

    # ── Step 1: Build synthetic raw data ─────────────────────────────────────
    print("  [1/2] Generating sample financial data…")
    raw = build_sample_raw(ticker=ticker, n_quarters=n_quarters)
    print(f"        {len(raw['fiscalDates'])} fiscal quarters created "
          f"({raw['fiscalDates'][0]} → {raw['fiscalDates'][-1]})")

    # ── Step 2: Parse ─────────────────────────────────────────────────────────
    print("  [2/3] Parsing & calculating metrics…")
    parsed = build_parsed_data(raw)
    print(f"        chartData: {len(parsed['chartData'])} rows, "
          f"{len(parsed['availableMetrics'])} metrics available")

    # ── Step 3: Build offline HTML ────────────────────────────────────────────
    print("  [3/3] Injecting data into React template…")
    if output is None:
        ts = int(time.time())
        output = REPO_ROOT / "reports" / f"demo_{ticker}_{ts}.html"

    result_path = generate_static_html(
        parsed,
        output_path=output,
        template_path=TEMPLATE_PATH,
    )

    size_kb = result_path.stat().st_size / 1024
    print(f"\n✅  Demo report ready: {result_path}  ({size_kb:.0f} KB)")
    print("    Open this file in any browser — no internet connection required.")
    return result_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--ticker", "-t",
        default="DEMO",
        help="Ticker symbol shown in the dashboard header (default: DEMO)",
    )
    parser.add_argument(
        "--quarters", "-q",
        type=int,
        default=80,
        help="Number of quarters to generate (min 52, default: 80)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Destination HTML file path (default: reports/demo_<ticker>_<ts>.html)",
    )
    args = parser.parse_args()

    if args.quarters < 52:
        parser.error("--quarters must be at least 52 (13 years)")

    if not TEMPLATE_PATH.exists():
        print("⚠  React build not found.  Building now…")
        import subprocess
        ui_dir = REPO_ROOT / "src" / "ui"
        if not (ui_dir / "node_modules").exists():
            subprocess.run(["npm", "install"], cwd=ui_dir, check=True)
        subprocess.run(["npm", "run", "build"], cwd=ui_dir, check=True)

    generate_demo(
        ticker=args.ticker.upper(),
        n_quarters=args.quarters,
        output=args.output,
    )


if __name__ == "__main__":
    main()
