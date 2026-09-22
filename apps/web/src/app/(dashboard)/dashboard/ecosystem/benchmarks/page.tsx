"use client";
/** Benchmark Lab: suites, runs, dimension comparison (Part F). */

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill, StatWithCI } from "../components";
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

interface LeaderboardRow {
  entity_kind: string;
  entity_id: string;
  canonical_name: string;
  run_id: string;
  finished_at: string | null;
  total_cost_usd: number;
  on_frontier?: boolean;
  dimension_scores: Record<string, number | null>;
  dimension_stats: Record<string, { mean: number; n: number; ci95: [number, number] }>;
}

const LEADERBOARD_DIMENSIONS = [
  "reliability",
  "cost_per_case_usd",
  "speed_p50_ms",
  "human_pref_elo",
  "text_accuracy",
];

const FAMILIES = [
  "ecommerce_hero",
  "product_consistency",
  "character_consistency",
  "chinese_text_render",
  "storyboard_adherence",
  "i2v_motion",
  "temporal_consistency",
  "commercial_ad_15s",
  "background_replacement",
  "multimodal_qa",
];

export default function BenchmarksPage() {
  const [selectedSuite, setSelectedSuite] = useState<string | null>(null);
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [lbFamily, setLbFamily] = useState("");
  const [lbDimension, setLbDimension] = useState("reliability");
  const leaderboard = useQuery({
    queryKey: ["eco-leaderboard", lbFamily, lbDimension],
    queryFn: () =>
      apiWithAuth<{ data: { rows: LeaderboardRow[] } }>(
        `/ecosystem/benchmark/leaderboard?dimension=${lbDimension}${
          lbFamily ? `&family=${lbFamily}` : ""
        }`,
      ),
  });

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
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <h2 className="text-lg font-semibold">Leaderboard</h2>
          <select
            value={lbFamily}
            onChange={(e) => setLbFamily(e.target.value)}
            className="rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-sm"
          >
            <option value="">All families</option>
            {FAMILIES.map((f) => (
              <option key={f}>{f}</option>
            ))}
          </select>
          <select
            value={lbDimension}
            onChange={(e) => setLbDimension(e.target.value)}
            className="rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-sm"
          >
            {LEADERBOARD_DIMENSIONS.map((d) => (
              <option key={d}>{d}</option>
            ))}
          </select>
          <span className="text-xs text-[hsl(var(--muted-foreground))]">
            latest completed run per model — dimensions never collapsed
          </span>
        </div>
        {(leaderboard.data?.data.rows ?? []).length === 0 ? (
          <EmptyState icon="🏆" text="No completed runs yet for this selection." />
        ) : (
          <div className="overflow-x-auto rounded-lg border shadow-sm">
            <table className="w-full">
              <thead className="bg-[hsl(var(--secondary))]">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">#</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Model</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">{lbDimension}</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Reliability</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Cost/case</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">p50 ms</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Elo</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {(leaderboard.data?.data.rows ?? []).map((row, i) => (
                  <tr key={row.run_id} className="bg-[hsl(var(--card))]">
                    <td className="px-4 py-3 text-sm font-bold">{i + 1}</td>
                    <td className="px-4 py-3 text-sm font-medium">
                      {row.canonical_name}
                      {row.on_frontier && (
                        <span
                          title="Pareto frontier: no other entity is both better and cheaper"
                          className="ml-1 text-xs text-amber-500"
                        >
                          ★ frontier
                        </span>
                      )}
                      <span className="ml-1 text-xs text-[hsl(var(--muted-foreground))]">
                        ({row.entity_kind})
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm font-semibold">
                      {row.dimension_scores?.[lbDimension] != null
                        ? Number(row.dimension_scores[lbDimension]).toFixed(4)
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <StatWithCI stats={row.dimension_stats?.reliability} digits={2} />
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <StatWithCI stats={row.dimension_stats?.cost_usd} digits={4} />
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <StatWithCI stats={row.dimension_stats?.latency_ms} digits={0} />
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {row.dimension_scores?.human_pref_elo != null
                        ? Number(row.dimension_scores.human_pref_elo).toFixed(0)
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

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
