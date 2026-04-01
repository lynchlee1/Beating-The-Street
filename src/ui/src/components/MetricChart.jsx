import React, { useMemo } from "react";
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { thinData, fmtMoney, fmtValue, dateToQuarterLabel, paletteColor } from "../utils/dataUtils.js";

const styles = {
  wrapper: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius)",
    padding: "16px",
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    minHeight: 0,
  },
  title: {
    fontWeight: 700,
    fontSize: "13px",
    color: "var(--text-dim)",
    letterSpacing: ".5px",
    textTransform: "uppercase",
  },
};

/** Custom tooltip renderer for Recharts. */
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div
      style={{
        background: "var(--surface2)",
        border: "1px solid var(--border)",
        borderRadius: "8px",
        padding: "10px 14px",
        fontSize: "12px",
        color: "var(--text)",
        maxWidth: 240,
      }}
    >
      <div style={{ fontWeight: 700, marginBottom: 6, color: "var(--text-dim)" }}>
        {label}
      </div>
      {payload.map((entry) => (
        <div key={entry.name} style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
          <span style={{ color: entry.color }}>● {entry.name}</span>
          <span style={{ fontWeight: 600 }}>
            {fmtValue(entry.value, entry.unit)}
          </span>
        </div>
      ))}
    </div>
  );
}

/**
 * MetricChart — a responsive time-series chart for one or more metrics.
 *
 * Props:
 *   title       string
 *   chartData   array of chart data objects
 *   metrics     array of { key, label, unit, color?, type? ("line"|"bar") }
 *   trailingMode "1Q" | "4Q" | "12Q"
 */
export default function MetricChart({ title, chartData, metrics, trailingMode = "4Q" }) {
  const data = useMemo(() => {
    const thinned = thinData(chartData, 80);
    return thinned.map((row) => {
      const point = { date: dateToQuarterLabel(row.date) };
      for (const m of metrics) {
        const key =
          trailingMode === "4Q"
            ? `${m.key}_4q`
            : trailingMode === "12Q"
            ? `${m.key}_12q`
            : m.key;
        point[m.label] = row[key] ?? null;
      }
      return point;
    });
  }, [chartData, metrics, trailingMode]);

  // Detect if we need a second Y axis (mix of % and $ for example)
  const hasSecondAxis = metrics.some((m) => m.axis === 2);

  return (
    <div style={styles.wrapper}>
      {title && <div style={styles.title}>{title}</div>}
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={data} margin={{ top: 6, right: hasSecondAxis ? 50 : 10, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.07)" />
          <XAxis
            dataKey="date"
            tick={{ fill: "var(--text-dim)", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            yAxisId={1}
            tick={{ fill: "var(--text-dim)", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => fmtMoney(v)}
            width={55}
          />
          {hasSecondAxis && (
            <YAxis
              yAxisId={2}
              orientation="right"
              tick={{ fill: "var(--text-dim)", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => fmtValue(v, metrics.find((m) => m.axis === 2)?.unit)}
              width={55}
            />
          )}
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 11, color: "var(--text-dim)" }}
            iconType="plainline"
            iconSize={14}
          />
          <ReferenceLine yAxisId={1} y={0} stroke="rgba(255,255,255,.15)" strokeDasharray="4 4" />
          {metrics.map((m, idx) => {
            const color = m.color || paletteColor(idx);
            const yAxisId = m.axis || 1;
            if (m.type === "bar") {
              return (
                <Bar
                  key={m.key}
                  dataKey={m.label}
                  fill={color}
                  fillOpacity={0.7}
                  yAxisId={yAxisId}
                  unit={m.unit}
                  radius={[2, 2, 0, 0]}
                />
              );
            }
            return (
              <Line
                key={m.key}
                type="monotone"
                dataKey={m.label}
                stroke={color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
                yAxisId={yAxisId}
                unit={m.unit}
                connectNulls={false}
              />
            );
          })}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
