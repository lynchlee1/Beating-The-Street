import React from "react";
import MetricChart from "./MetricChart.jsx";
import StatsTable from "./StatsTable.jsx";
import ValuationPanel from "./ValuationPanel.jsx";

const S = {
  section: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  twoCol: {
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: "12px",
  },
};

/** Standard section layouts for each tab */

export function ValuationDashboard({ chartData, averages, growth, valuation, trailingMode }) {
  return (
    <div style={S.section}>
      <ValuationPanel valuation={valuation} />
      <div style={S.twoCol}>
        <MetricChart
          title="P/E Ratio"
          chartData={chartData}
          trailingMode={trailingMode}
          metrics={[
            { key: "per", label: "P/E Ratio", unit: "x", color: "#4f8ef7" },
          ]}
        />
        <MetricChart
          title="Market Cap"
          chartData={chartData}
          trailingMode={trailingMode}
          metrics={[
            { key: "marketCap", label: "Market Cap", unit: "$", color: "#f5a623" },
          ]}
        />
      </div>
    </div>
  );
}

export function OperationsDashboard({ chartData, averages, growth, trailingMode }) {
  return (
    <div style={S.section}>
      <div style={S.twoCol}>
        <MetricChart
          title="Revenue & Net Income"
          chartData={chartData}
          trailingMode={trailingMode}
          metrics={[
            { key: "revenue",    label: "Revenue",     unit: "$", color: "#4f8ef7" },
            { key: "netIncome",  label: "Net Income",  unit: "$", color: "#56c99c" },
            { key: "netIncomeCO", label: "Cont. Net Income", unit: "$", color: "#4ec9e8" },
          ]}
        />
        <MetricChart
          title="EPS & Dividends"
          chartData={chartData}
          trailingMode={trailingMode}
          metrics={[
            { key: "epsDiluted", label: "Diluted EPS",    unit: "$", color: "#4f8ef7" },
            { key: "eps",        label: "EPS",            unit: "$", color: "#90caf9" },
            { key: "dividends",  label: "Dividends",      unit: "$", color: "#f5a623", type: "bar" },
          ]}
        />
      </div>
      <StatsTable
        title="Operations Averages"
        averages={averages}
        growth={growth}
        rows={[
          { key: "revenue",   label: "Revenue",     unit: "$", showGrowth: true },
          { key: "netIncome", label: "Net Income",  unit: "$", showGrowth: true },
          { key: "epsDiluted",label: "Diluted EPS", unit: "$", showGrowth: true },
          { key: "dividends", label: "Dividends",   unit: "$" },
          { key: "dividendYield", label: "Dividend Yield", unit: "%" },
          { key: "payoutRatio",   label: "Payout Ratio",  unit: "%" },
        ]}
      />
    </div>
  );
}

export function StabilityDashboard({ chartData, averages, growth, trailingMode }) {
  return (
    <div style={S.section}>
      <div style={S.twoCol}>
        <MetricChart
          title="Shares Outstanding"
          chartData={chartData}
          trailingMode={trailingMode}
          metrics={[
            { key: "shares",        label: "Basic Shares",    unit: "#", color: "#4f8ef7" },
            { key: "sharesDiluted", label: "Diluted Shares",  unit: "#", color: "#90caf9" },
          ]}
        />
        <MetricChart
          title="Cash Flow"
          chartData={chartData}
          trailingMode={trailingMode}
          metrics={[
            { key: "freeCashFlow", label: "Free Cash Flow", unit: "$", color: "#4f8ef7" },
            { key: "cfo",          label: "Operating CF",   unit: "$", color: "#4ec9e8" },
            { key: "cff",          label: "Financing CF",   unit: "$", color: "#f5a623" },
          ]}
        />
      </div>
      <StatsTable
        title="Stability Averages"
        averages={averages}
        growth={growth}
        rows={[
          { key: "shares",        label: "Shares Outstanding", unit: "#", showGrowth: true },
          { key: "sharesDiluted", label: "Diluted Shares",     unit: "#", showGrowth: true },
          { key: "freeCashFlow",  label: "Free Cash Flow",     unit: "$", showGrowth: true },
          { key: "cfo",           label: "Operating CF",       unit: "$" },
        ]}
      />
    </div>
  );
}

export function CapitalDashboard({ chartData, averages, growth, trailingMode }) {
  return (
    <div style={S.section}>
      <div style={S.twoCol}>
        <MetricChart
          title="Debt & Cash"
          chartData={chartData}
          trailingMode={trailingMode}
          metrics={[
            { key: "cash",         label: "Cash",          unit: "$", color: "#56c99c" },
            { key: "longTermDebt", label: "LT Debt",       unit: "$", color: "#ef5350" },
            { key: "netDebt",      label: "Net Debt",      unit: "$", color: "#f5a623" },
            { key: "inventory",    label: "Inventory",     unit: "$", color: "#ab7af8" },
          ]}
        />
        <MetricChart
          title="Capital Efficiency"
          chartData={chartData}
          trailingMode={trailingMode}
          metrics={[
            { key: "netMargin",    label: "Net Margin",    unit: "%", color: "#4f8ef7" },
            { key: "roe",          label: "ROE",           unit: "%", color: "#56c99c" },
            { key: "leverage",     label: "Leverage",      unit: "x", color: "#f5a623", axis: 2 },
          ]}
        />
      </div>
      <StatsTable
        title="Capital Structure Averages"
        averages={averages}
        growth={growth}
        rows={[
          { key: "netMargin",    label: "Net Margin",    unit: "%" },
          { key: "roe",          label: "ROE",           unit: "%" },
          { key: "assetTurnover",label: "Asset Turnover",unit: "x" },
          { key: "leverage",     label: "Leverage",      unit: "x" },
          { key: "debtToEquity", label: "Debt / Equity", unit: "x" },
        ]}
      />
    </div>
  );
}
