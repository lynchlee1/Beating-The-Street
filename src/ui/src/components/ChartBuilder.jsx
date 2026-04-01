import React, { useState, useMemo } from "react";
import MetricChart from "./MetricChart.jsx";
import { groupByCategory, paletteColor } from "../utils/dataUtils.js";

const S = {
  wrapper: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  header: {
    fontWeight: 700,
    fontSize: "15px",
    color: "var(--text)",
  },
  desc: {
    fontSize: "12px",
    color: "var(--text-dim)",
    marginTop: -8,
  },
  panels: {
    display: "grid",
    gridTemplateColumns: "280px 1fr",
    gap: "12px",
    alignItems: "start",
  },
  sidebar: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius)",
    padding: "12px",
    display: "flex",
    flexDirection: "column",
    gap: "4px",
    maxHeight: "70vh",
    overflowY: "auto",
  },
  categoryLabel: {
    fontSize: "10px",
    fontWeight: 700,
    color: "var(--accent)",
    textTransform: "uppercase",
    letterSpacing: ".6px",
    padding: "10px 4px 4px",
  },
  metricRow: (selected) => ({
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "6px 8px",
    borderRadius: "6px",
    cursor: "pointer",
    background: selected ? "rgba(79,142,247,.12)" : "transparent",
    border: selected ? "1px solid rgba(79,142,247,.3)" : "1px solid transparent",
    transition: "background .15s, border .15s",
    userSelect: "none",
  }),
  checkbox: {
    width: 14,
    height: 14,
    flexShrink: 0,
  },
  metricLabel: (selected) => ({
    fontSize: "12px",
    color: selected ? "var(--text)" : "var(--text-dim)",
    fontWeight: selected ? 600 : 400,
  }),
  colorDot: (color) => ({
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: color,
    flexShrink: 0,
    marginLeft: "auto",
  }),
  chartArea: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  emptyState: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius)",
    padding: "40px",
    textAlign: "center",
    color: "var(--text-dim)",
    fontSize: "13px",
  },
  trailSelector: {
    display: "flex",
    gap: "6px",
    flexWrap: "wrap",
  },
  chip: (active) => ({
    padding: "5px 12px",
    borderRadius: "999px",
    border: `1px solid ${active ? "var(--accent)" : "var(--border)"}`,
    background: active ? "rgba(79,142,247,.15)" : "transparent",
    color: active ? "var(--accent)" : "var(--text-dim)",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: active ? 700 : 400,
    transition: "all .15s",
  }),
  clearBtn: {
    marginLeft: "auto",
    padding: "5px 12px",
    borderRadius: "999px",
    border: "1px solid var(--border)",
    background: "transparent",
    color: "var(--text-dim)",
    cursor: "pointer",
    fontSize: "12px",
  },
};

const TRAILING_MODES = ["1Q", "4Q", "12Q"];
const TRAILING_LABELS = { "1Q": "Quarterly", "4Q": "Trailing 1Y", "12Q": "Trailing 3Y" };
const MAX_SELECTED = 8;

/**
 * ChartBuilder — interactive metric selection for custom chart creation.
 *
 * Props:
 *   chartData        array from parsed data
 *   availableMetrics array from parsed data
 */
export default function ChartBuilder({ chartData, availableMetrics }) {
  const [selected, setSelected] = useState([]);
  const [trailingMode, setTrailingMode] = useState("4Q");

  const groups = useMemo(() => groupByCategory(availableMetrics), [availableMetrics]);

  const toggle = (metric) => {
    setSelected((prev) => {
      const exists = prev.find((m) => m.key === metric.key);
      if (exists) return prev.filter((m) => m.key !== metric.key);
      if (prev.length >= MAX_SELECTED) return prev; // max 8
      return [...prev, metric];
    });
  };

  // Assign a stable color per selected metric
  const metricsWithColor = useMemo(
    () => selected.map((m, i) => ({ ...m, color: paletteColor(i) })),
    [selected]
  );

  return (
    <div style={S.wrapper}>
      <div>
        <div style={S.header}>Custom Chart Builder</div>
        <div style={S.desc}>
          Select up to {MAX_SELECTED} metrics from the panel to overlay them on a single chart.
        </div>
      </div>

      {/* Trailing mode selector */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
        <span style={{ fontSize: "12px", color: "var(--text-dim)", fontWeight: 600 }}>View:</span>
        <div style={S.trailSelector}>
          {TRAILING_MODES.map((mode) => (
            <button
              key={mode}
              style={S.chip(trailingMode === mode)}
              onClick={() => setTrailingMode(mode)}
            >
              {TRAILING_LABELS[mode]}
            </button>
          ))}
        </div>
        {selected.length > 0 && (
          <button style={S.clearBtn} onClick={() => setSelected([])}>
            Clear all
          </button>
        )}
      </div>

      <div style={S.panels}>
        {/* Metric selector sidebar */}
        <div style={S.sidebar}>
          {Object.entries(groups).map(([category, metrics]) => (
            <React.Fragment key={category}>
              <div style={S.categoryLabel}>{category}</div>
              {metrics.map((m, i) => {
                const isSelected = selected.some((s) => s.key === m.key);
                const colorIdx = selected.findIndex((s) => s.key === m.key);
                const color = colorIdx >= 0 ? paletteColor(colorIdx) : "transparent";
                return (
                  <div
                    key={m.key}
                    style={S.metricRow(isSelected)}
                    onClick={() => toggle(m)}
                    role="checkbox"
                    aria-checked={isSelected}
                    tabIndex={0}
                    onKeyDown={(e) => e.key === "Enter" && toggle(m)}
                  >
                    <input
                      type="checkbox"
                      readOnly
                      checked={isSelected}
                      style={S.checkbox}
                      tabIndex={-1}
                    />
                    <span style={S.metricLabel(isSelected)}>{m.label}</span>
                    {isSelected && <div style={S.colorDot(color)} />}
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>

        {/* Chart area */}
        <div style={S.chartArea}>
          {metricsWithColor.length === 0 ? (
            <div style={S.emptyState}>
              ← Select one or more metrics to visualise them here.
            </div>
          ) : (
            <MetricChart
              title={metricsWithColor.map((m) => m.label).join(" · ")}
              chartData={chartData}
              trailingMode={trailingMode}
              metrics={metricsWithColor}
            />
          )}
        </div>
      </div>
    </div>
  );
}
