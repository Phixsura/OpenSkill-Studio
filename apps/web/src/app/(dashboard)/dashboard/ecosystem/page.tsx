"use client";
/** Ecosystem Intelligence — operator overview (ADR-016 Part P/S). */

import { useQuery } from "@tanstack/react-query";
import { apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill, StatCard } from "./components";
import { SEVERITY_STYLES, fmtDate } from "./lib";

interface Overview {
  sources: { active: number; paused: number; error: number };
  discoveries_7d: number;
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
            <StatCard label="Discoveries (7d)" value={overview.discoveries_7d} />
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
