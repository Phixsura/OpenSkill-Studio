"use client";
/** Snapshot matrix — provenance-backed sufficient statistics per metric ×
 * variant × UTC-day window (ADR-017 Part L). */

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiWithAuth } from "@/lib/api";
import { EmptyState, ExperimentsNav, SectionCard } from "../../components";
import { fmtDate, fmtNum, type MetricSnapshot } from "../../lib";

/** Daily value per variant for the sparkline: rate when the row carries a
 * denominator, mean when it carries n+sum, else null (skipped). */
function rowValue(s: MetricSnapshot): number | null {
  if (s.denominator) return (s.numerator ?? 0) / s.denominator;
  if (s.n && s.sum_value != null) return s.sum_value / s.n;
  return null;
}

const SPARK_COLORS = ["#0f172a", "#2563eb", "#d97706", "#059669", "#dc2626"];

function Sparkline({ rows }: { rows: MetricSnapshot[] }) {
  // whole-population rows only, grouped by variant, ordered by window
  const series: Record<string, { t: number; v: number }[]> = {};
  for (const s of rows) {
    if (s.segment) continue;
    const v = rowValue(s);
    if (v == null) continue;
    (series[s.variant_key] ??= []).push({ t: Date.parse(s.window_start), v });
  }
  const variants = Object.keys(series).sort();
  const points = variants.flatMap((k) => series[k] ?? []);
  if (points.length < 2) return null;
  const ts = points.map((p) => p.t);
  const vs = points.map((p) => p.v);
  const [t0, t1] = [Math.min(...ts), Math.max(...ts)];
  const [v0, v1] = [Math.min(...vs), Math.max(...vs)];
  const sx = (t: number) => (t1 === t0 ? 0 : ((t - t0) / (t1 - t0)) * 220) + 2;
  const sy = (v: number) => 34 - (v1 === v0 ? 17 : ((v - v0) / (v1 - v0)) * 32);
  return (
    <div className="mb-2 flex items-center gap-4" data-testid="metric-sparkline">
      <svg width="224" height="36" aria-hidden className="shrink-0">
        {variants.map((variant, i) => (
          <polyline
            key={variant}
            fill="none"
            stroke={SPARK_COLORS[i % SPARK_COLORS.length]}
            strokeWidth="1.5"
            points={(series[variant] ?? [])
              .sort((a, b) => a.t - b.t)
              .map((p) => `${sx(p.t).toFixed(1)},${sy(p.v).toFixed(1)}`)
              .join(" ")}
          />
        ))}
      </svg>
      <div className="text-xs text-slate-500">
        {variants.map((variant, i) => (
          <span key={variant} className="mr-3">
            <span
              className="mr-1 inline-block h-2 w-2 rounded-full align-middle"
              style={{ backgroundColor: SPARK_COLORS[i % SPARK_COLORS.length] }}
            />
            {variant}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function ExperimentMetricsPage() {
  const { experimentId } = useParams<{ experimentId: string }>();
  const { data, isLoading } = useQuery({
    queryKey: ["experiment-snapshots", experimentId],
    queryFn: () =>
      apiWithAuth<{ data: MetricSnapshot[] }>(`/experiments/${experimentId}/metrics?limit=500`),
  });

  const snapshots = data?.data ?? [];
  const byMetric = snapshots.reduce<Record<string, MetricSnapshot[]>>((acc, s) => {
    (acc[s.metric_key] ??= []).push(s);
    return acc;
  }, {});

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <h1 className="text-xl font-semibold">
        <Link href={`/dashboard/experiments/${experimentId}`} className="hover:underline">
          Experiment
        </Link>{" "}
        · Metric snapshots
      </h1>
      {isLoading ? (
        <div className="text-sm text-slate-500">Loading…</div>
      ) : snapshots.length === 0 ? (
        <EmptyState message="No snapshots yet — the daily window sweep populates this once the experiment is running." />
      ) : (
        Object.entries(byMetric).map(([metric, rows]) => (
          <SectionCard key={metric} title={metric}>
            <Sparkline rows={rows} />
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-left text-xs uppercase text-slate-500">
                  <tr>
                    <th className="py-1 pr-3">Window</th>
                    <th className="py-1 pr-3">Variant</th>
                    <th className="py-1 pr-3">Segment</th>
                    <th className="py-1 pr-3">n</th>
                    <th className="py-1 pr-3">Numerator</th>
                    <th className="py-1 pr-3">Denominator</th>
                    <th className="py-1 pr-3">Sum</th>
                    <th className="py-1 pr-3">Source · qv</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((s) => (
                    <tr key={s.id} className="border-t">
                      <td className="whitespace-nowrap py-1 pr-3 text-xs text-slate-500">
                        {fmtDate(s.window_start)}
                      </td>
                      <td className="py-1 pr-3 font-medium">{s.variant_key}</td>
                      <td className="py-1 pr-3 text-xs text-slate-500">{s.segment || "whole"}</td>
                      <td className="py-1 pr-3">{s.n}</td>
                      <td className="py-1 pr-3">{fmtNum(s.numerator, 2)}</td>
                      <td className="py-1 pr-3">{fmtNum(s.denominator, 2)}</td>
                      <td className="py-1 pr-3">{fmtNum(s.sum_value, 2)}</td>
                      <td className="py-1 pr-3 text-xs text-slate-500">
                        {s.provenance?.source ?? "—"} · v{s.provenance?.query_version ?? "?"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SectionCard>
        ))
      )}
    </div>
  );
}
