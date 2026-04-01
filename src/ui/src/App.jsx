import React, { useState, useEffect } from "react";
import {
  ValuationDashboard,
  OperationsDashboard,
  StabilityDashboard,
  CapitalDashboard,
} from "./components/Dashboard.jsx";
import ChartBuilder from "./components/ChartBuilder.jsx";

/* ─── Sample data for development / preview ─────────────────────────────── */
const MOCK_DATA = (() => {
  const dates = [];
  const base = new Date("2012-03-31");
  for (let i = 0; i < 48; i++) {
    const d = new Date(base);
    d.setMonth(base.getMonth() + i * 3);
    dates.push(d.toISOString().split("T")[0]);
  }

  const rand = (min, max) => min + Math.random() * (max - min);
  const chartData = dates.map((date, i) => {
    const growth = 1 + i * 0.018;
    return {
      date,
      revenue:     rand(800, 1200) * 1e6 * growth,
      netIncome:   rand(80,  140)  * 1e6 * growth,
      netIncomeCO: rand(70,  130)  * 1e6 * growth,
      eps:         rand(1.5, 2.5) * growth,
      epsDiluted:  rand(1.4, 2.4) * growth,
      shares:      rand(200, 230) * 1e6,
      sharesDiluted: rand(210, 240) * 1e6,
      dividends:   rand(0.2, 0.5),
      cash:        rand(500, 900) * 1e6,
      longTermDebt: rand(200, 400) * 1e6,
      netDebt:     rand(-200, 100) * 1e6,
      inventory:   rand(50, 150) * 1e6,
      cfo:         rand(100, 200) * 1e6 * growth,
      cff:         rand(-150, -50) * 1e6,
      freeCashFlow: rand(60, 160) * 1e6 * growth,
      marketCap:   rand(5, 8) * 1e9 * growth,
      // 4Q trailing (annualised)
      revenue_4q:       rand(3000, 4500) * 1e6 * growth,
      netIncome_4q:     rand(320,  550)  * 1e6 * growth,
      netIncomeCO_4q:   rand(300,  530)  * 1e6 * growth,
      eps_4q:           rand(6,    10) * growth,
      epsDiluted_4q:    rand(5.5,  9.5) * growth,
      shares_4q:        rand(200, 230) * 1e6,
      sharesDiluted_4q: rand(210, 240) * 1e6,
      dividends_4q:     rand(0.8, 2.0),
      dividendYield_4q: rand(0.01, 0.03),
      payoutRatio_4q:   rand(0.1, 0.4),
      cash_4q:          rand(500, 900) * 1e6,
      longTermDebt_4q:  rand(200, 400) * 1e6,
      netDebt_4q:       rand(-200, 100) * 1e6,
      inventory_4q:     rand(50, 150) * 1e6,
      netMargin_4q:     rand(0.08, 0.15),
      roe_4q:           rand(0.1, 0.25),
      assetTurnover_4q: rand(0.5, 1.5),
      leverage_4q:      rand(1.5, 3.5),
      debtToEquity_4q:  rand(0.3, 0.9),
      cfo_4q:           rand(400, 800) * 1e6 * growth,
      cff_4q:           rand(-600, -200) * 1e6,
      freeCashFlow_4q:  rand(240, 640) * 1e6 * growth,
      per_4q:           rand(10, 25),
      marketCap_4q:     rand(5, 8) * 1e9 * growth,
      // 12Q trailing
      revenue_12q:       rand(9000, 13500) * 1e6 * growth,
      netIncome_12q:     rand(960,  1650)  * 1e6 * growth,
      netIncomeCO_12q:   rand(900,  1590)  * 1e6 * growth,
      eps_12q:           rand(5,    9) * growth,
      epsDiluted_12q:    rand(4.5,  8.5) * growth,
      shares_12q:        rand(200, 230) * 1e6,
      sharesDiluted_12q: rand(210, 240) * 1e6,
      dividends_12q:     rand(0.7, 1.8),
      dividendYield_12q: rand(0.01, 0.025),
      payoutRatio_12q:   rand(0.1, 0.35),
      cash_12q:          rand(500, 900) * 1e6,
      longTermDebt_12q:  rand(200, 400) * 1e6,
      netDebt_12q:       rand(-200, 100) * 1e6,
      inventory_12q:     rand(50, 150) * 1e6,
      netMargin_12q:     rand(0.07, 0.13),
      roe_12q:           rand(0.09, 0.22),
      assetTurnover_12q: rand(0.5, 1.4),
      leverage_12q:      rand(1.5, 3.0),
      debtToEquity_12q:  rand(0.3, 0.8),
      cfo_12q:           rand(1200, 2400) * 1e6 * growth,
      cff_12q:           rand(-1800, -600) * 1e6,
      freeCashFlow_12q:  rand(720, 1920) * 1e6 * growth,
      per_12q:           rand(10, 22),
      marketCap_12q:     rand(5, 8) * 1e9 * growth,
    };
  });

  const last = chartData[chartData.length - 1];
  const makeAvg = (key) => ({
    "3Y":  last[`${key}_4q`] * rand(0.85, 0.95),
    "5Y":  last[`${key}_4q`] * rand(0.80, 0.90),
    "10Y": last[`${key}_4q`] * rand(0.70, 0.82),
    "13Y": last[`${key}_4q`] * rand(0.65, 0.78),
    "20Y": last[`${key}_4q`] * rand(0.55, 0.70),
  });
  const makeGrowth = () => ({
    "3Y":  rand(0.05, 0.15),
    "5Y":  rand(0.06, 0.13),
    "10Y": rand(0.07, 0.12),
    "13Y": rand(0.06, 0.11),
    "20Y": rand(0.05, 0.10),
  });

  return {
    ticker: "DEMO",
    generatedAt: new Date().toISOString(),
    fiscalDates: dates,
    chartData,
    availableMetrics: [
      { key: "revenue",       label: "Revenue",           category: "Income",    unit: "$" },
      { key: "netIncome",     label: "Net Income",        category: "Income",    unit: "$" },
      { key: "netIncomeCO",   label: "Cont. Net Income",  category: "Income",    unit: "$" },
      { key: "eps",           label: "EPS",               category: "Per Share", unit: "$" },
      { key: "epsDiluted",    label: "Diluted EPS",       category: "Per Share", unit: "$" },
      { key: "dividends",     label: "Dividends",         category: "Per Share", unit: "$" },
      { key: "dividendYield", label: "Dividend Yield",    category: "Per Share", unit: "%" },
      { key: "payoutRatio",   label: "Payout Ratio",      category: "Per Share", unit: "%" },
      { key: "shares",        label: "Shares",            category: "Shares",    unit: "#" },
      { key: "sharesDiluted", label: "Diluted Shares",    category: "Shares",    unit: "#" },
      { key: "freeCashFlow",  label: "Free Cash Flow",    category: "Cash Flow", unit: "$" },
      { key: "cfo",           label: "Operating CF",      category: "Cash Flow", unit: "$" },
      { key: "cff",           label: "Financing CF",      category: "Cash Flow", unit: "$" },
      { key: "cash",          label: "Cash & Equiv.",     category: "Balance",   unit: "$" },
      { key: "longTermDebt",  label: "LT Debt",           category: "Balance",   unit: "$" },
      { key: "netDebt",       label: "Net Debt",          category: "Balance",   unit: "$" },
      { key: "inventory",     label: "Inventory",         category: "Balance",   unit: "$" },
      { key: "netMargin",     label: "Net Margin",        category: "Ratios",    unit: "%" },
      { key: "roe",           label: "ROE",               category: "Ratios",    unit: "%" },
      { key: "assetTurnover", label: "Asset Turnover",    category: "Ratios",    unit: "x" },
      { key: "leverage",      label: "Leverage",          category: "Ratios",    unit: "x" },
      { key: "debtToEquity",  label: "Debt / Equity",     category: "Ratios",    unit: "x" },
      { key: "per",           label: "P/E Ratio",         category: "Valuation", unit: "x" },
      { key: "marketCap",     label: "Market Cap",        category: "Valuation", unit: "$" },
    ],
    averages: Object.fromEntries(
      ["revenue","netIncome","netIncomeCO","eps","epsDiluted","shares","sharesDiluted",
       "dividends","dividendYield","payoutRatio","cash","longTermDebt","netDebt",
       "inventory","netMargin","roe","assetTurnover","leverage","debtToEquity",
       "cfo","cff","freeCashFlow","per","marketCap"]
      .map((k) => [k, makeAvg(k)])
    ),
    growth: Object.fromEntries(
      ["revenue","netIncome","eps","epsDiluted","shares","sharesDiluted","freeCashFlow"]
      .map((k) => [k, makeGrowth()])
    ),
    valuation: {
      currentMarketCap:  last.marketCap * 4,
      currentStockPrice: rand(40, 120),
      per: rand(0.03, 0.07),
      cashPerStock: rand(-5, 20),
      cashPercent: rand(-0.05, 0.15),
      boxGroups: Object.fromEntries(
        ["3Y","5Y","10Y","13Y","20Y"].map((lbl) => [lbl, {
          netIncome: last.netIncome_4q * rand(0.7, 1.0),
          eps:       last.eps_4q * last.shares_4q * rand(0.7, 1.0),
          py:        last.netIncome_4q * rand(0.3, 0.6),
        }])
      ),
      peg:         Object.fromEntries(["3Y","5Y","10Y","13Y","20Y"].map((l) => [l, rand(0.5, 2.5)])),
      adjustedPeg: Object.fromEntries(["3Y","5Y","10Y","13Y","20Y"].map((l) => [l, rand(0.4, 2.0)])),
    },
  };
})();

/* ─── Styles ─────────────────────────────────────────────────────────────── */
const S = {
  app: {
    display: "grid",
    gridTemplateRows: "auto auto 1fr",
    height: "100dvh",
    gap: "0",
    overflow: "hidden",
  },
  header: {
    padding: "10px 16px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    borderBottom: "1px solid var(--border)",
    background: "var(--surface)",
    gap: "12px",
    flexWrap: "wrap",
  },
  brand: {
    fontWeight: 800,
    fontSize: "17px",
    letterSpacing: ".3px",
    color: "var(--text)",
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  ticker: {
    fontSize: "22px",
    fontWeight: 900,
    color: "var(--accent)",
    letterSpacing: "1px",
  },
  meta: {
    fontSize: "11px",
    color: "var(--text-dim)",
  },
  nav: {
    padding: "0 16px",
    display: "flex",
    gap: "4px",
    borderBottom: "1px solid var(--border)",
    background: "var(--surface)",
    overflowX: "auto",
    scrollbarWidth: "none",
  },
  navTab: (active) => ({
    padding: "10px 14px",
    cursor: "pointer",
    color: active ? "var(--accent)" : "var(--text-dim)",
    fontWeight: active ? 700 : 400,
    fontSize: "13px",
    userSelect: "none",
    whiteSpace: "nowrap",
    transition: "color .15s",
    background: "none",
    border: "none",
    borderBottom: active ? "2px solid var(--accent)" : "2px solid transparent",
  }),
  toolbar: {
    display: "flex",
    gap: "6px",
    alignItems: "center",
  },
  chip: (active) => ({
    padding: "5px 11px",
    borderRadius: "999px",
    border: `1px solid ${active ? "var(--accent)" : "var(--border)"}`,
    background: active ? "rgba(79,142,247,.15)" : "transparent",
    color: active ? "var(--accent)" : "var(--text-dim)",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: active ? 700 : 400,
    transition: "all .15s",
    whiteSpace: "nowrap",
  }),
  downloadBtn: {
    padding: "6px 14px",
    borderRadius: "999px",
    background: "linear-gradient(135deg, rgba(79,142,247,.25), rgba(86,201,156,.15))",
    border: "1px solid rgba(79,142,247,.4)",
    color: "var(--accent)",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: 700,
    transition: "all .2s",
    whiteSpace: "nowrap",
  },
  main: {
    overflowY: "auto",
    padding: "16px",
  },
  notice: {
    background: "rgba(245,166,35,.08)",
    border: "1px solid rgba(245,166,35,.3)",
    borderRadius: "8px",
    padding: "10px 14px",
    fontSize: "12px",
    color: "var(--warn)",
    marginBottom: "12px",
  },
};

const TABS = [
  { id: "valuation",  label: "Valuation" },
  { id: "operations", label: "Operations" },
  { id: "stability",  label: "Financial Stability" },
  { id: "capital",    label: "Capital Structure" },
  { id: "builder",    label: "📊 Chart Builder" },
];

const TRAILING_MODES = [
  { id: "1Q",  label: "Quarterly" },
  { id: "4Q",  label: "Trailing 1Y" },
  { id: "12Q", label: "Trailing 3Y" },
];

export default function App() {
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState("valuation");
  const [trailingMode, setTrailingMode] = useState("4Q");
  const [isMock, setIsMock] = useState(false);

  useEffect(() => {
    if (window.__INITIAL_DATA__) {
      setData(window.__INITIAL_DATA__);
    } else {
      // Dev/preview: use mock data
      setData(MOCK_DATA);
      setIsMock(true);
    }
  }, []);

  if (!data) {
    return (
      <div style={{ display: "grid", placeItems: "center", height: "100dvh" }}>
        <div style={{ color: "var(--text-dim)", fontSize: "14px" }}>Loading…</div>
      </div>
    );
  }

  const { ticker, generatedAt, chartData, availableMetrics, averages, growth, valuation } = data;

  /** Download the current page as an offline HTML file. */
  const handleDownload = () => {
    const html = document.documentElement.outerHTML;
    const blob = new Blob([html], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report_${ticker}_${Date.now()}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const generatedDate = generatedAt
    ? new Date(generatedAt).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })
    : "";

  return (
    <div style={S.app}>
      {/* ── Header ── */}
      <header style={S.header}>
        <div style={S.brand}>
          <span>Beating The Street</span>
          <span style={S.ticker}>{ticker}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          {generatedDate && (
            <span style={S.meta}>Generated: {generatedDate}</span>
          )}
          {/* Trailing mode chips (only for non-builder tabs) */}
          {activeTab !== "builder" && (
            <div style={S.toolbar}>
              {TRAILING_MODES.map((m) => (
                <button
                  key={m.id}
                  style={S.chip(trailingMode === m.id)}
                  onClick={() => setTrailingMode(m.id)}
                >
                  {m.label}
                </button>
              ))}
            </div>
          )}
          <button style={S.downloadBtn} onClick={handleDownload}>
            ⬇ Download
          </button>
        </div>
      </header>

      {/* ── Navigation tabs ── */}
      <nav style={S.nav} aria-label="Dashboard sections">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            style={S.navTab(activeTab === tab.id)}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* ── Main content ── */}
      <main style={S.main}>
        {isMock && (
          <div style={S.notice}>
            ⚠ Showing demo data. Run <code>python run.py TICKER</code> to generate a real report.
          </div>
        )}

        {activeTab === "valuation" && (
          <ValuationDashboard
            chartData={chartData}
            averages={averages}
            growth={growth}
            valuation={valuation}
            trailingMode={trailingMode}
          />
        )}
        {activeTab === "operations" && (
          <OperationsDashboard
            chartData={chartData}
            averages={averages}
            growth={growth}
            trailingMode={trailingMode}
          />
        )}
        {activeTab === "stability" && (
          <StabilityDashboard
            chartData={chartData}
            averages={averages}
            growth={growth}
            trailingMode={trailingMode}
          />
        )}
        {activeTab === "capital" && (
          <CapitalDashboard
            chartData={chartData}
            averages={averages}
            growth={growth}
            trailingMode={trailingMode}
          />
        )}
        {activeTab === "builder" && (
          <ChartBuilder chartData={chartData} availableMetrics={availableMetrics} />
        )}
      </main>
    </div>
  );
}
