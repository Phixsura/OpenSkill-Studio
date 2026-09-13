"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";
import { cn } from "@/lib/utils";

/* ── Types ───────────────────────────────────────────────── */

interface GapItem {
  capability_id: string;
  capability_name: string;
  demand_count: number;
  qualified_supply: number;
  gap: number;
  gap_severity: string;
  content_coverage: Record<string, number>;
}

interface CoverageItem {
  capability_id: string;
  capability_name: string;
  coverage_by_type: Record<string, number>;
  content: { source_type: string; source_id: string; weight: number }[];
}

interface PlacementAnalytics {
  applications_by_status: Record<string, number>;
  placements_by_status: Record<string, number>;
  total_applications: number;
  total_placements: number;
}

/* ── Helpers ─────────────────────────────────────────────── */

const SEVERITY_STYLES: Record<string, string> = {
  high: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
  medium: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
  low: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
};

function SeverityBadge({ severity }: { severity: string }) {
  return (
    <span
      className={cn(
        "inline-block rounded-full px-2.5 py-0.5 text-xs font-medium capitalize",
        SEVERITY_STYLES[severity] ?? "bg-gray-100 text-gray-700",
      )}
    >
      {severity}
    </span>
  );
}

/* ── Page ────────────────────────────────────────────────── */

export default function TalentDashboardPage() {
  const { data: gapsData, isLoading: gapsLoading } = useQuery({
    queryKey: ["talent-gaps"],
    queryFn: () => apiWithAuth<{ data: GapItem[] }>("/talent/intelligence/gaps?limit=10"),
  });

  const { data: coverageData, isLoading: coverageLoading } = useQuery({
    queryKey: ["talent-coverage"],
    queryFn: () => apiWithAuth<{ data: CoverageItem[] }>("/talent/intelligence/coverage?limit=8"),
  });

  const { data: placementsData, isLoading: placementsLoading } = useQuery({
    queryKey: ["talent-placements"],
    queryFn: () => apiWithAuth<{ data: PlacementAnalytics }>("/talent/intelligence/placements"),
  });

  const gaps = gapsData?.data ?? [];
  const coverage = coverageData?.data ?? [];
  const placements = placementsData?.data;

  const totalDemand = gaps.reduce((s, g) => s + g.demand_count, 0);
  const totalSupply = gaps.reduce((s, g) => s + g.qualified_supply, 0);
  const highGaps = gaps.filter((g) => g.gap_severity === "high").length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Talent Intelligence</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Workforce demand, verified supply, and curriculum coverage insights
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Demand" value={totalDemand} loading={gapsLoading} />
        <StatCard label="Verified Supply" value={totalSupply} loading={gapsLoading} />
        <StatCard
          label="Critical Gaps"
          value={highGaps}
          loading={gapsLoading}
          accent={highGaps > 0 ? "red" : undefined}
        />
        <StatCard
          label="Active Placements"
          value={placements?.total_placements ?? 0}
          loading={placementsLoading}
        />
      </div>

      {/* Quick nav */}
      <div className="flex flex-wrap gap-2">
        <Link
          href="/dashboard/talent/demand"
          className="rounded-md border px-3 py-1.5 text-sm hover:bg-[hsl(var(--secondary))]"
        >
          Demand detail →
        </Link>
        <Link
          href="/dashboard/talent/supply"
          className="rounded-md border px-3 py-1.5 text-sm hover:bg-[hsl(var(--secondary))]"
        >
          Supply detail →
        </Link>
      </div>

      {/* Demand-supply gap table */}
      <section>
        <h2 className="mb-3 text-lg font-semibold">Demand-Supply Gaps</h2>
        {gapsLoading ? (
          <Skeleton rows={5} />
        ) : gaps.length === 0 ? (
          <EmptyState message="No demand-supply gap data available yet." />
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-[hsl(var(--muted))]/50 text-left">
                  <th className="sticky top-0 bg-[hsl(var(--muted))]/50 px-4 py-3 font-medium">
                    Capability
                  </th>
                  <th className="sticky top-0 bg-[hsl(var(--muted))]/50 px-4 py-3 text-right font-medium">
                    Demand
                  </th>
                  <th className="sticky top-0 bg-[hsl(var(--muted))]/50 px-4 py-3 text-right font-medium">
                    Supply
                  </th>
                  <th className="sticky top-0 bg-[hsl(var(--muted))]/50 px-4 py-3 text-right font-medium">
                    Gap
                  </th>
                  <th className="sticky top-0 bg-[hsl(var(--muted))]/50 px-4 py-3 font-medium">
                    Severity
                  </th>
                </tr>
              </thead>
              <tbody>
                {gaps.map((g, i) => (
                  <tr
                    key={g.capability_id}
                    className={cn(
                      "border-b last:border-0",
                      i % 2 === 1 && "bg-[hsl(var(--muted))]/20",
                    )}
                  >
                    <td className="px-4 py-3 font-medium">{g.capability_name}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{g.demand_count}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{g.qualified_supply}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{g.gap}</td>
                    <td className="px-4 py-3">
                      <SeverityBadge severity={g.gap_severity} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Content coverage */}
      <section>
        <h2 className="mb-3 text-lg font-semibold">Content Coverage</h2>
        {coverageLoading ? (
          <Skeleton rows={3} />
        ) : coverage.length === 0 ? (
          <EmptyState message="No content coverage data available yet." />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {coverage.map((c) => {
              const types = c.coverage_by_type ?? {};
              const missingAssessment = !types.assessment_blueprint;
              const missingProject = !types.project_template;
              return (
                <div key={c.capability_id} className="rounded-lg border p-4">
                  <h3 className="font-medium">{c.capability_name}</h3>
                  <div className="mt-2 flex flex-wrap gap-1.5 text-xs">
                    {Object.entries(types).map(([type, count]) => (
                      <span
                        key={type}
                        className="rounded-md bg-[hsl(var(--secondary))] px-2 py-0.5"
                      >
                        {type.replace(/_/g, " ")}: {count}
                      </span>
                    ))}
                  </div>
                  {(missingAssessment || missingProject) && (
                    <div className="mt-2 flex flex-wrap gap-1.5 text-xs">
                      {missingAssessment && (
                        <span className="rounded-md bg-amber-100 px-2 py-0.5 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
                          No assessment
                        </span>
                      )}
                      {missingProject && (
                        <span className="rounded-md bg-amber-100 px-2 py-0.5 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
                          No project template
                        </span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Placement funnel */}
      <section>
        <h2 className="mb-3 text-lg font-semibold">Placement Funnel</h2>
        {placementsLoading ? (
          <Skeleton rows={2} />
        ) : !placements ? (
          <EmptyState message="No placement data available yet." />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(placements.applications_by_status).map(([status, count]) => (
              <div key={status} className="rounded-lg border p-4">
                <p className="text-sm capitalize text-[hsl(var(--muted-foreground))]">
                  {status.replace(/_/g, " ")}
                </p>
                <p className="mt-1 text-2xl font-bold tabular-nums">{count}</p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

/* ── Shared components ───────────────────────────────────── */

function StatCard({
  label,
  value,
  loading,
  accent,
}: {
  label: string;
  value: number;
  loading?: boolean;
  accent?: "red";
}) {
  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-5">
      <p className="text-sm text-[hsl(var(--muted-foreground))]">{label}</p>
      {loading ? (
        <div className="mt-2 h-8 w-16 animate-pulse rounded bg-[hsl(var(--muted))]" />
      ) : (
        <p
          className={cn(
            "mt-1 text-3xl font-bold tabular-nums",
            accent === "red" && "text-red-600 dark:text-red-400",
          )}
        >
          {value}
        </p>
      )}
    </div>
  );
}

function Skeleton({ rows }: { rows: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-10 animate-pulse rounded bg-[hsl(var(--muted))]" />
      ))}
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-dashed p-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
      {message}
    </div>
  );
}
