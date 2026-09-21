"use client";
/** Benchmark Lab: suites, runs, dimension comparison (Part F). */

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill } from "../components";
import { STATUS_STYLES, fmtDate } from "../lib";

interface Suite {
  id: string;
  key: string;
  name: string;
  family: string;
  capability_key: string;
  budget_usd_cap: number;
  repeat_count: number;
  status: string;
}

interface Run {
  id: string;
  suite_id: string;
  status: string;
  target: { entity_kind?: string; entity_id?: string };
  total_cost_usd: number;
  dimension_scores: Record<string, number | null>;
  created_at: string;
}

interface Comparison {
  runs: {
    run_id: string;
    target: { entity_id?: string };
    dimension_scores: Record<string, number | null>;
    total_cost_usd: number;
  }[];
  dimensions: string[];
}

export default function BenchmarksPage() {
  const [selectedSuite, setSelectedSuite] = useState<string | null>(null);
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [error, setError] = useState<string | null>(null);

  const suites = useQuery({
    queryKey: ["eco-suites"],
    queryFn: () => apiWithAuth<{ data: Suite[] }>("/ecosystem/benchmark/suites"),
  });
  const runs = useQuery({
    queryKey: ["eco-runs", selectedSuite],
    queryFn: () =>
      apiWithAuth<{ data: Run[] }>(
        `/ecosystem/benchmark/runs?limit=50${selectedSuite ? `&suite_id=${selectedSuite}` : ""}`,
      ),
  });

  const compare = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: Comparison }>(
        `/ecosystem/benchmark/runs/compare?ids=${compareIds.join(",")}`,
      ),
    onSuccess: (res) => {
      setComparison(res.data);
      setError(null);
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Comparison failed"),
  });

  const toggleCompare = (id: string) =>
    setCompareIds((ids) =>
      ids.includes(id) ? ids.filter((x) => x !== id) : ids.length < 6 ? [...ids, id] : ids,
    );

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Benchmark Lab</h1>
      <EcosystemNav />
      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <section>
        <h2 className="mb-3 text-lg font-semibold">Suites</h2>
        {(suites.data?.data ?? []).length === 0 ? (
          <EmptyState icon="🧪" text="No benchmark suites yet." />
        ) : (
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {(suites.data?.data ?? []).map((s) => (
              <button
                key={s.id}
                onClick={() => setSelectedSuite(selectedSuite === s.id ? null : s.id)}
                className={`rounded-lg border p-4 text-left shadow-sm ${
                  selectedSuite === s.id
                    ? "border-[hsl(var(--primary))] bg-[hsl(var(--secondary))]"
                    : "bg-[hsl(var(--card))]"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold">{s.name}</span>
                  <Pill value={s.status} styles={STATUS_STYLES} />
                </div>
                <div className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                  {s.family} · {s.capability_key} · ×{s.repeat_count} · cap $
                  {Number(s.budget_usd_cap).toFixed(2)}
                </div>
              </button>
            ))}
          </div>
        )}
      </section>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            Runs {selectedSuite ? "(filtered by suite)" : ""}
          </h2>
          <button
            disabled={compareIds.length < 2 || compare.isPending}
            onClick={() => compare.mutate()}
            className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm text-[hsl(var(--primary-foreground))] disabled:opacity-50"
          >
            Compare selected ({compareIds.length})
          </button>
        </div>
        {(runs.data?.data ?? []).length === 0 ? (
          <EmptyState icon="🏁" text="No runs yet." />
        ) : (
          <div className="overflow-x-auto rounded-lg border shadow-sm">
            <table className="w-full">
              <thead className="bg-[hsl(var(--secondary))]">
                <tr>
                  <th className="px-4 py-3" />
                  <th className="px-4 py-3 text-left text-sm font-medium">Target</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Cost</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Reliability</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">p50 latency</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {(runs.data?.data ?? []).map((r) => (
                  <tr key={r.id} className="bg-[hsl(var(--card))]">
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={compareIds.includes(r.id)}
                        onChange={() => toggleCompare(r.id)}
                        disabled={r.status !== "completed" && !compareIds.includes(r.id)}
                      />
                    </td>
                    <td className="px-4 py-3 font-mono text-xs">
                      {r.target?.entity_kind}:{(r.target?.entity_id ?? "").slice(0, 10)}…
                    </td>
                    <td className="px-4 py-3">
                      <Pill value={r.status} styles={STATUS_STYLES} />
                    </td>
                    <td className="px-4 py-3 text-sm">${Number(r.total_cost_usd).toFixed(4)}</td>
                    <td className="px-4 py-3 text-sm">
                      {r.dimension_scores?.reliability != null
                        ? `${(Number(r.dimension_scores.reliability) * 100).toFixed(0)}%`
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {r.dimension_scores?.speed_p50_ms != null
                        ? `${r.dimension_scores.speed_p50_ms} ms`
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-sm text-[hsl(var(--muted-foreground))]">
                      {fmtDate(r.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {comparison && (
        <section>
          <h2 className="mb-3 text-lg font-semibold">
            Run comparison{" "}
            <span className="text-sm font-normal text-[hsl(var(--muted-foreground))]">
              — dimensions are preserved, never collapsed into one score
            </span>
          </h2>
          <div className="overflow-x-auto rounded-lg border shadow-sm">
            <table className="w-full">
              <thead className="bg-[hsl(var(--secondary))]">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">Dimension</th>
                  {comparison.runs.map((r) => (
                    <th key={r.run_id} className="px-4 py-3 text-left font-mono text-xs">
                      {(r.target?.entity_id ?? r.run_id).slice(0, 10)}…
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y">
                {comparison.dimensions.map((dim) => (
                  <tr key={dim} className="bg-[hsl(var(--card))]">
                    <td className="px-4 py-3 text-sm font-medium">{dim}</td>
                    {comparison.runs.map((r) => (
                      <td key={r.run_id} className="px-4 py-3 text-sm">
                        {r.dimension_scores?.[dim] != null
                          ? Number(r.dimension_scores[dim]).toFixed(4)
                          : "—"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
