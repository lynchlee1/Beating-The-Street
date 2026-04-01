import React, { useMemo } from "react";
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from "recharts";
import { fmtMoney, fmtValue, fmtPeg, WINDOW_LABELS } from "../utils/dataUtils.js";

const S = {
  wrapper: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius)",
    padding: "16px",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  title: {
    fontWeight: 700,
    fontSize: "13px",
    color: "var(--text-dim)",
    letterSpacing: ".5px",
    textTransform: "uppercase",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "12px",
  },
  card: {
    background: "var(--surface2)",
    border: "1px solid var(--border)",
    borderRadius: "8px",
    padding: "12px 14px",
  },
  cardLabel: {
    fontSize: "11px",
    color: "var(--text-dim)",
    textTransform: "uppercase",
    letterSpacing: ".5px",
    marginBottom: "4px",
  },
  cardValue: {
    fontSize: "20px",
    fontWeight: 700,
    color: "var(--text)",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: "12px",
  },
  th: {
    padding: "6px 10px",
    textAlign: "right",
    fontWeight: 700,
    color: "var(--text-dim)",
    background: "var(--surface2)",
    borderBottom: "1px solid var(--border)",
  },
  thLabel: { textAlign: "left" },
  td: {
    padding: "6px 10px",
    textAlign: "right",
    borderBottom: "1px solid rgba(255,255,255,.04)",
    color: "var(--text)",
  },
  tdLabel: { textAlign: "left", color: "var(--text-dim)" },
};

const BOX_COLORS = {
  netIncome: "#56c99c",
  eps:       "#f5a623",
  py:        "#ef5350",
};

/**
 * ValuationPanel — displays the "Beating the Street" valuation view.
 *
 * Shows:
 *  - Key stats (PER, Market Cap, Cash per share)
 *  - Valuation band chart (box-whisker style for 3Y/5Y/10Y/13Y/20Y)
 *  - PEG table
 */
export default function ValuationPanel({ valuation }) {
  const { currentMarketCap, currentStockPrice, per, cashPerStock, cashPercent,
          boxGroups, peg, adjustedPeg } = valuation;

  // Build bar chart data from boxGroups
  const barData = useMemo(
    () =>
      WINDOW_LABELS.map((lbl) => {
        const g = boxGroups[lbl] || {};
        return {
          period: lbl,
          // Each metric represents the "fair value" midpoint; whiskers at 8x and 18x
          netIncome_low:  (g.netIncome || 0) * 8,
          netIncome_mid:  (g.netIncome || 0) * 13,
          netIncome_high: (g.netIncome || 0) * 18,
          eps_low:        (g.eps || 0) * 8,
          eps_mid:        (g.eps || 0) * 13,
          eps_high:       (g.eps || 0) * 18,
          py_low:         (g.py || 0) * 8,
          py_mid:         (g.py || 0) * 13,
          py_high:        (g.py || 0) * 18,
        };
      }),
    [boxGroups]
  );

  // Simplified valuation range chart: show the midpoint bars + current mcap line
  const chartData = useMemo(
    () =>
      WINDOW_LABELS.map((lbl) => {
        const g = boxGroups[lbl] || {};
        return {
          period: lbl,
          "NI Valuation":  (g.netIncome || null) ? g.netIncome * 13 : null,
          "EPS Valuation": (g.eps || null) ? g.eps * 13 : null,
          "PY Valuation":  (g.py || null) ? g.py * 13 : null,
        };
      }),
    [boxGroups]
  );

  return (
    <div style={S.wrapper}>
      <div style={S.title}>Valuation Overview</div>

      {/* Key stats */}
      <div style={S.grid}>
        <div style={S.card}>
          <div style={S.cardLabel}>Market Cap</div>
          <div style={S.cardValue}>{fmtMoney(currentMarketCap)}</div>
        </div>
        <div style={S.card}>
          <div style={S.cardLabel}>Stock Price</div>
          <div style={S.cardValue}>${(currentStockPrice || 0).toFixed(2)}</div>
        </div>
        <div style={S.card}>
          <div style={S.cardLabel}>P/E Ratio (adjusted)</div>
          <div style={S.cardValue}>{per ? (per * 4).toFixed(1) : "N/A"}</div>
        </div>
        <div style={S.card}>
          <div style={S.cardLabel}>Net Cash / Share</div>
          <div style={{ ...S.cardValue, color: cashPerStock >= 0 ? "var(--accent2)" : "var(--danger)" }}>
            {cashPerStock >= 0 ? `$${cashPerStock.toFixed(2)}` : `-$${Math.abs(cashPerStock).toFixed(2)}`}
            {cashPercent ? ` (${(cashPercent * 100).toFixed(1)}%)` : ""}
          </div>
        </div>
      </div>

      {/* Valuation band chart */}
      <div style={{ fontWeight: 600, fontSize: "12px", color: "var(--text-dim)" }}>
        Implied Market Cap (13× Fair Earnings) vs Current
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <ComposedChart data={chartData} margin={{ top: 6, right: 10, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.07)" />
          <XAxis dataKey="period" tick={{ fill: "var(--text-dim)", fontSize: 11 }} tickLine={false} axisLine={false} />
          <YAxis tick={{ fill: "var(--text-dim)", fontSize: 10 }} tickLine={false} axisLine={false}
            tickFormatter={fmtMoney} width={55} />
          <Tooltip formatter={(v) => fmtMoney(v)} />
          <Legend wrapperStyle={{ fontSize: 11, color: "var(--text-dim)" }} />
          <Bar dataKey="NI Valuation"  fill={BOX_COLORS.netIncome} fillOpacity={0.75} radius={[3,3,0,0]} />
          <Bar dataKey="EPS Valuation" fill={BOX_COLORS.eps}       fillOpacity={0.75} radius={[3,3,0,0]} />
          <Bar dataKey="PY Valuation"  fill={BOX_COLORS.py}        fillOpacity={0.75} radius={[3,3,0,0]} />
          <ReferenceLine y={currentMarketCap} stroke="var(--accent)" strokeWidth={2}
            strokeDasharray="5 3" label={{ value: "Cur. MCap", fill: "var(--accent)", fontSize: 10 }} />
        </ComposedChart>
      </ResponsiveContainer>

      {/* PEG table */}
      <div style={{ fontWeight: 600, fontSize: "12px", color: "var(--text-dim)", marginTop: 4 }}>
        PEG Ratios
      </div>
      <table style={S.table}>
        <thead>
          <tr>
            <th style={{ ...S.th, ...S.thLabel }}></th>
            {WINDOW_LABELS.map((w) => <th key={w} style={S.th}>{w}</th>)}
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style={S.tdLabel}>PEG Ratio</td>
            {WINDOW_LABELS.map((w) => (
              <td key={w} style={S.td}>{fmtPeg(peg?.[w])}</td>
            ))}
          </tr>
          <tr>
            <td style={S.tdLabel}>Adjusted PEG</td>
            {WINDOW_LABELS.map((w) => (
              <td key={w} style={S.td}>{fmtPeg(adjustedPeg?.[w])}</td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
