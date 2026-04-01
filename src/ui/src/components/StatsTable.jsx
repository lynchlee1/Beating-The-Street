import React from "react";
import { fmtValue, fmtGrowth, WINDOW_LABELS } from "../utils/dataUtils.js";

const S = {
  wrapper: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius)",
    overflow: "hidden",
  },
  title: {
    padding: "10px 14px 6px",
    fontWeight: 700,
    fontSize: "12px",
    color: "var(--text-dim)",
    letterSpacing: ".5px",
    textTransform: "uppercase",
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
    whiteSpace: "nowrap",
  },
  thLabel: {
    textAlign: "left",
  },
  td: {
    padding: "6px 10px",
    textAlign: "right",
    borderBottom: "1px solid rgba(255,255,255,.04)",
    whiteSpace: "nowrap",
    color: "var(--text)",
  },
  tdLabel: {
    textAlign: "left",
    color: "var(--text-dim)",
    fontWeight: 500,
  },
  tdLabelIndent: {
    textAlign: "left",
    color: "var(--text-dim)",
    paddingLeft: "24px",
    fontStyle: "italic",
  },
  sectionRow: {
    background: "rgba(79,142,247,.06)",
    fontWeight: 700,
    color: "var(--accent)",
    padding: "5px 10px",
    fontSize: "11px",
    letterSpacing: ".4px",
  },
};

/** A table row for a single metric showing multi-period averages (and optional growth). */
function MetricRow({ label, averages, growth, unit, isGrowthRow = false }) {
  const indented = isGrowthRow;
  return (
    <tr>
      <td style={indented ? S.tdLabelIndent : S.tdLabel}>
        {indented ? "↳ Growth" : label}
      </td>
      {WINDOW_LABELS.map((w) => {
        const val = isGrowthRow ? growth?.[w] : averages?.[w];
        const displayVal = isGrowthRow ? fmtGrowth(val) : fmtValue(val, unit);
        return (
          <td key={w} style={S.td}>
            {displayVal}
          </td>
        );
      })}
    </tr>
  );
}

/**
 * StatsTable — multi-period averages table.
 *
 * Props:
 *   title      string
 *   rows       array of { key, label, unit, showGrowth? }
 *   averages   object (from parsed data)
 *   growth     object (from parsed data)
 */
export default function StatsTable({ title, rows, averages, growth }) {
  return (
    <div style={S.wrapper}>
      {title && <div style={S.title}>{title}</div>}
      <table style={S.table}>
        <thead>
          <tr>
            <th style={{ ...S.th, ...S.thLabel }}></th>
            {WINDOW_LABELS.map((w) => (
              <th key={w} style={S.th}>{w}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <React.Fragment key={row.key}>
              <MetricRow
                label={row.label}
                averages={averages[row.key]}
                growth={growth[row.key]}
                unit={row.unit}
              />
              {row.showGrowth && growth[row.key] && (
                <MetricRow
                  label={row.label}
                  averages={averages[row.key]}
                  growth={growth[row.key]}
                  unit="%"
                  isGrowthRow
                />
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
