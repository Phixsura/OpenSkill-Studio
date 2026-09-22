"use client";
/** Ecosystem Intelligence — operator overview (ADR-016 Part P/S). */

import { useQuery } from "@tanstack/react-query";
import { apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill, StatCard } from "./components";
import { SEVERITY_STYLES, fmtDate } from "./lib";

interface Overview {
  sources: { active: number; paused: number; error: number };
  sources_stale: number;
  discoveries_7d: number;
  observations_unverified: number;
  injection_flagged_unverified: number;
  changes_unacknowledged: number;
  security_critical_open: number;
  pricing_unreviewed: number;
  resolution_pending: number;
  benchmark_queue: number;
  impact_open: number;
  replacements_proposed: number;
  drafts_in_review: number;
  rollouts_active: number;
}

interface ChangeEvent {
  id: string;
  change_type: string;
  field: string;
  severity: string;
  entity_kind: string | null;
  detected_at: string;
  acknowledged: boolean;
}

export default function EcosystemOverviewPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["eco-dashboard"],
    queryFn: () => apiWithAuth<{ data: Overview }>("/ecosystem/dashboard"),
  });
  const coverage = useQuery({
    queryKey: ["eco-coverage"],
    queryFn: () =>
      apiWithAuth<{
        data: Record<
          string,
          {
            total: number;
            with_capability_mapping: number;
            with_benchmark: number;
            with_pricing: number;
          }
        >;
      }>("/ecosystem/dashboard/coverage"),
  });
  const trending = useQuery({
    queryKey: ["eco-trending"],
    queryFn: () =>
      apiWithAuth<{
        data: {
          entity_kind: string;
          entity_id: string;
          canonical_name: string;
          observations: number;
          distinct_sources: number;
          velocity: number | null;
        }[];
      }>("/ecosystem/dashboard/trending?days=7&limit=8"),
  });
  const feed = useQuery({
    queryKey: ["eco-feed-preview"],
    queryFn: () =>
      apiWithAuth<{ data: ChangeEvent[] }>("/ecosystem/dashboard/change-feed?limit=10"),
  });

  if (isError) return <div className="p-8 text-center text-red-600">Failed to load data</div>;
  const overview = data?.data;

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold">Ecosystem Intelligence</h1>
        <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
          Continuous external capability discovery, benchmarking and component lifecycle
        </p>
      </div>
      <EcosystemNav />
      {isLoading || !overview ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading overview…</div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
            <StatCard label="Active sources" value={overview.sources.active} />
            <StatCard
              label="Paused / errored sources"
              value={overview.sources.paused + overview.sources.error}
              alert={overview.sources.error > 0}
            />
            <StatCard
              label="Stale sources (3× interval)"
              value={overview.sources_stale}
              alert={overview.sources_stale > 0}
            />
            <StatCard label="Discoveries (7d)" value={overview.discoveries_7d} />
            <StatCard
              label="Unverified observations"
              value={overview.observations_unverified}
              alert={overview.observations_unverified > 50}
            />
            <StatCard
              label="Injection-flagged (advisory)"
              value={overview.injection_flagged_unverified}
              alert={overview.injection_flagged_unverified > 0}
            />
            <StatCard
              label="Unacknowledged changes"
              value={overview.changes_unacknowledged}
              alert={overview.changes_unacknowledged > 0}
            />
            <StatCard
              label="Security critical open"
              value={overview.security_critical_open}
              alert={overview.security_critical_open > 0}
            />
            <StatCard label="Pricing to review" value={overview.pricing_unreviewed} />
            <StatCard label="Resolution queue" value={overview.resolution_pending} />
            <StatCard label="Benchmark queue" value={overview.benchmark_queue} />
            <StatCard label="Open impact analyses" value={overview.impact_open} />
            <StatCard label="Replacement proposals" value={overview.replacements_proposed} />
            <StatCard label="Drafts in review" value={overview.drafts_in_review} />
            <StatCard label="Active rollouts" value={overview.rollouts_active} />
          </div>
          {(trending.data?.data ?? []).length > 0 && (
            <div>
              <h2 className="mb-3 text-lg font-semibold">Trending (7d observation velocity)</h2>
              <div className="flex flex-wrap gap-2">
                {(trending.data?.data ?? []).map((t) => (
                  <span
                    key={t.entity_id}
                    className="rounded-full border bg-[hsl(var(--card))] px-3 py-1 text-xs shadow-sm"
                    title={`${t.observations} observations from ${t.distinct_sources} sources`}
                  >
                    {t.canonical_name}
                    <span className="ml-1 text-[hsl(var(--muted-foreground))]">
                      ({t.entity_kind}) ·{" "}
                      {t.velocity === null ? "new" : `${t.velocity}× vs prior week`}
                    </span>
                  </span>
                ))}
              </div>
            </div>
          )}
          <div>
            <h2 className="mb-3 text-lg font-semibold">Catalog coverage</h2>
            <div className="overflow-x-auto rounded-lg border shadow-sm">
              <table className="w-full text-sm">
                <thead className="bg-[hsl(var(--secondary))]">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium">Kind</th>
                    <th className="px-4 py-2 text-left text-xs font-medium">Total</th>
                    <th className="px-4 py-2 text-left text-xs font-medium">Capability-mapped</th>
                    <th className="px-4 py-2 text-left text-xs font-medium">Benchmarked</th>
                    <th className="px-4 py-2 text-left text-xs font-medium">Priced</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {Object.entries(coverage.data?.data ?? {}).map(([kind, c]) => (
                    <tr key={kind} className="bg-[hsl(var(--card))]">
                      <td className="px-4 py-2 font-medium">{kind}</td>
                      <td className="px-4 py-2">{c.total}</td>
                      <td className="px-4 py-2">
                        {c.with_capability_mapping}
                        {c.total > 0 &&
                          ` (${Math.round((100 * c.with_capability_mapping) / c.total)}%)`}
                      </td>
                      <td className="px-4 py-2">
                        {c.with_benchmark}
                        {c.total > 0 && ` (${Math.round((100 * c.with_benchmark) / c.total)}%)`}
                      </td>
                      <td className="px-4 py-2">
                        {c.with_pricing}
                        {c.total > 0 && ` (${Math.round((100 * c.with_pricing) / c.total)}%)`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div>
            <h2 className="mb-3 text-lg font-semibold">Latest changes</h2>
            {(feed.data?.data ?? []).length === 0 ? (
              <EmptyState
                icon="🛰️"
                text="No external changes observed yet. Register a source to start discovering."
              />
            ) : (
              <div className="overflow-hidden rounded-lg border shadow-sm">
                <table className="w-full">
                  <thead className="bg-[hsl(var(--secondary))]">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Field</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Severity</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Detected</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {(feed.data?.data ?? []).map((c) => (
                      <tr key={c.id} className="bg-[hsl(var(--card))]">
                        <td className="px-4 py-3 text-sm font-medium">{c.change_type}</td>
                        <td className="px-4 py-3 text-sm">{c.field}</td>
                        <td className="px-4 py-3">
                          <Pill value={c.severity} styles={SEVERITY_STYLES} />
                        </td>
                        <td className="px-4 py-3 text-sm text-[hsl(var(--muted-foreground))]">
                          {fmtDate(c.detected_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
