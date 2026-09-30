"use client";
/** Snapshot matrix — provenance-backed sufficient statistics per metric ×
 * variant × UTC-day window (ADR-017 Part L). */

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiWithAuth } from "@/lib/api";
import { EmptyState, ExperimentsNav, SectionCard } from "../../components";
import { fmtDate, fmtNum, type MetricSnapshot } from "../../lib";

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
