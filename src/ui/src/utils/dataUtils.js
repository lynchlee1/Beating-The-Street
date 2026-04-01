/**
 * Data utility functions for the Beating-The-Street dashboard.
 */

/** Format a raw number as a compact financial string (e.g. 1.2B, 34.5M, 12.3K). */
export function fmtMoney(value, decimals = 1) {
  if (value === null || value === undefined || !isFinite(value)) return "N/A";
  const abs = Math.abs(value);
  const sign = value < 0 ? "-" : "";
  if (abs >= 1e12) return `${sign}${(abs / 1e12).toFixed(decimals)}T`;
  if (abs >= 1e9)  return `${sign}${(abs / 1e9).toFixed(decimals)}B`;
  if (abs >= 1e6)  return `${sign}${(abs / 1e6).toFixed(decimals)}M`;
  if (abs >= 1e3)  return `${sign}${(abs / 1e3).toFixed(decimals)}K`;
  return `${sign}${abs.toFixed(decimals)}`;
}

/** Format a ratio as a percentage string. */
export function fmtPct(value, decimals = 2) {
  if (value === null || value === undefined || !isFinite(value)) return "N/A";
  return `${(value * 100).toFixed(decimals)}%`;
}

/** Format a ratio as a multiplier string (e.g. 1.23x). */
export function fmtX(value, decimals = 2) {
  if (value === null || value === undefined || !isFinite(value)) return "N/A";
  return `${value.toFixed(decimals)}x`;
}

/** Format a number for display based on metric unit. */
export function fmtValue(value, unit) {
  if (value === null || value === undefined || !isFinite(value)) return "N/A";
  switch (unit) {
    case "%": return fmtPct(value);
    case "x": return fmtX(value);
    case "#": return fmtMoney(value, 2);
    default:  return fmtMoney(value);
  }
}

/**
 * Return the appropriate series key for a metric given a trailing mode.
 * mode: "1Q" | "4Q" | "12Q"
 */
export function seriesKey(metricKey, mode) {
  if (mode === "4Q")  return `${metricKey}_4q`;
  if (mode === "12Q") return `${metricKey}_12q`;
  return metricKey; // raw quarterly
}

/** Group available metrics by category. */
export function groupByCategory(metrics) {
  const groups = {};
  for (const m of metrics) {
    if (!groups[m.category]) groups[m.category] = [];
    groups[m.category].push(m);
  }
  return groups;
}

/** Pick a stable color from a palette for a given index. */
const PALETTE = [
  "#4f8ef7", "#56c99c", "#f5a623", "#ef5350", "#ab7af8",
  "#4ec9e8", "#f06292", "#aed651", "#ff8a65", "#90caf9",
];

export function paletteColor(index) {
  return PALETTE[index % PALETTE.length];
}

/** Convert ISO date string "YYYY-MM-DD" to short display label "Q1 2020". */
export function dateToQuarterLabel(dateStr) {
  if (!dateStr) return "";
  const [year, month] = dateStr.split("-").map(Number);
  const q = Math.ceil(month / 3);
  return `Q${q} ${year}`;
}

/** Thin chartData to at most maxPoints evenly-spaced entries. */
export function thinData(chartData, maxPoints = 80) {
  if (chartData.length <= maxPoints) return chartData;
  const step = Math.ceil(chartData.length / maxPoints);
  return chartData.filter((_, i) => i % step === 0 || i === chartData.length - 1);
}

/** Return WINDOW_LABELS in display order. */
export const WINDOW_LABELS = ["3Y", "5Y", "10Y", "13Y", "20Y"];

/** Format a growth rate (raw fraction) as a percentage string. */
export function fmtGrowth(value) {
  if (value === null || value === undefined || !isFinite(value)) return "N/A";
  const pct = (value * 100).toFixed(2);
  return `${pct}%`;
}

/** Format a PEG ratio raw float. */
export function fmtPeg(value) {
  if (value === null || value === undefined || !isFinite(value)) return "N/A";
  return value.toFixed(2);
}
