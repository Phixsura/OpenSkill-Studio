"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

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

/* ── Custom Recharts Tooltip ──────────────────────────────── */

function DemandSupplyTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  const demand = payload.find((p) => p.name === "Demand")?.value ?? 0;
  const supply = payload.find((p) => p.name === "Supply")?.value ?? 0;
  const gap = demand - supply;
  const gapPct = demand > 0 ? Math.round((gap / demand) * 100) : 0;

  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-3 shadow-lg">
      <p className="mb-1.5 text-sm font-semibold">{label}</p>
      <div className="space-y-1 text-xs">
        <p className="flex items-center gap-1.5">
          <span className="inline-block h-2 w-2 rounded-sm bg-blue-500" />
          Demand: <span className="font-bold tabular-nums">{demand}</span>
        </p>
        <p className="flex items-center gap-1.5">
          <span className="inline-block h-2 w-2 rounded-sm bg-emerald-500" />
          Supply: <span className="font-bold tabular-nums">{supply}</span>
        </p>
        <p
          className={cn(
            "mt-1 border-t pt-1 font-medium",
            gapPct > 50
              ? "text-red-600 dark:text-red-400"
              : gapPct > 25
                ? "text-amber-600 dark:text-amber-400"
                : "text-emerald-600 dark:text-emerald-400",
          )}
        >
          Gap: {gap} ({gapPct}%)
        </p>
      </div>
    </div>
  );
}

/* ── Demand vs Supply Bar Chart (Recharts) ────────────────── */

function DemandSupplyChart({ gaps }: { gaps: GapItem[] }) {
  if (gaps.length === 0) return null;

  const chartData = gaps.map((g) => ({
    name: g.capability_name.length > 20 ? g.capability_name.slice(0, 18) + "…" : g.capability_name,
    fullName: g.capability_name,
    Demand: g.demand_count,
    Supply: g.qualified_supply,
    severity: g.gap_severity,
  }));

  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-5 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">Demand vs Supply</h3>
      <ResponsiveContainer width="100%" height={Math.max(gaps.length * 52, 200)}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 4, right: 30, left: 10, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis type="number" tick={{ fontSize: 11 }} />
          <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11 }} />
          <Tooltip content={<DemandSupplyTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="Demand" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={14} />
          <Bar dataKey="Supply" fill="#10b981" radius={[0, 4, 4, 0]} barSize={14} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

/* ── Pipeline Funnel (Recharts) ───────────────────────────── */

const PIPELINE_COLORS: Record<string, string> = {
  Applied: "#3b82f6",
  Screening: "#eab308",
  Interview: "#a855f7",
  Offer: "#22c55e",
  Hired: "#059669",
};

function PipelineFunnel({ placements }: { placements: PlacementAnalytics }) {
  const statusMap = placements.applications_by_status;

  const stageEntries = [
    { key: "submitted", label: "Applied" },
    { key: "screening", label: "Screening" },
    { key: "interview", label: "Interview" },
    { key: "offer", label: "Offer" },
    { key: "hired", label: "Hired" },
  ];

  const chartData = stageEntries.map((s, i) => {
    const count = statusMap[s.key] ?? 0;
    const prevKey = i > 0 ? stageEntries[i - 1]?.key : undefined;
    const prevCount = prevKey ? (statusMap[prevKey] ?? 0) : 0;
    const convRate = i > 0 && prevCount > 0 ? Math.round((count / prevCount) * 100) : null;
    return {
      stage: s.label,
      count,
      convRate,
    };
  });

  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-5 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">Placement Pipeline</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 4, right: 30, left: 10, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis type="number" tick={{ fontSize: 11 }} />
          <YAxis type="category" dataKey="stage" width={80} tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              fontSize: "12px",
              border: "1px solid hsl(var(--border))",
              backgroundColor: "hsl(var(--card))",
            }}
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            formatter={(value: any, _name: any, props: any) => {
              const convRate = props?.payload?.convRate;
              return [`${value}${convRate != null ? ` (${convRate}% conversion)` : ""}`, "Count"];
            }}
          />
          <Bar
            dataKey="count"
            radius={[0, 6, 6, 0]}
            barSize={24}
            label={{ position: "right", fontSize: 11, fontWeight: 600 }}
          >
            {chartData.map((entry) => (
              <Cell key={entry.stage} fill={PIPELINE_COLORS[entry.stage] ?? "#6b7280"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Summary stats */}
      <div className="mt-4 grid grid-cols-3 gap-3 border-t pt-4 text-center text-xs">
        <div>
          <p className="font-medium text-[hsl(var(--muted-foreground))]">Total Apps</p>
          <p className="mt-0.5 text-lg font-bold tabular-nums">{placements.total_applications}</p>
        </div>
        <div>
          <p className="font-medium text-[hsl(var(--muted-foreground))]">Placements</p>
          <p className="mt-0.5 text-lg font-bold tabular-nums">{placements.total_placements}</p>
        </div>
        <div>
          <p className="font-medium text-[hsl(var(--muted-foreground))]">Hire Rate</p>
          <p className="mt-0.5 text-lg font-bold tabular-nums">
            {placements.total_applications > 0
              ? `${Math.round(
                  (placements.total_placements / placements.total_applications) * 100,
                )}%`
              : "—"}
          </p>
        </div>
      </div>
    </div>
  );
}

/* ── Page ────────────────────────────────────────────────── */

export default function TalentDashboardPage() {
  const {
    data: gapsData,
    isLoading: gapsLoading,
    isError,
  } = useQuery({
    queryKey: ["talent-gaps"],
    queryFn: () => apiWithAuth<{ data: GapItem[] }>("/talent/intelligence/gaps?limit=10"),
  });

  const {
    data: coverageData,
    isLoading: coverageLoading,
    isError: _isErr2,
  } = useQuery({
    queryKey: ["talent-coverage"],
    queryFn: () => apiWithAuth<{ data: CoverageItem[] }>("/talent/intelligence/coverage?limit=8"),
  });

  const {
    data: placementsData,
    isLoading: placementsLoading,
    isError: _isErr3,
  } = useQuery({
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

      {/* Charts row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Demand vs Supply chart */}
        {gapsLoading ? (
          <div className="h-80 animate-pulse rounded-lg border bg-[hsl(var(--card))]" />
        ) : (
          <DemandSupplyChart gaps={gaps} />
        )}

        {/* Pipeline funnel */}
        {placementsLoading ? (
          <div className="h-80 animate-pulse rounded-lg border bg-[hsl(var(--card))]" />
        ) : placements ? (
          <PipelineFunnel placements={placements} />
        ) : (
          <div className="flex items-center justify-center rounded-lg border border-dashed p-8">
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              No placement data available yet.
            </p>
          </div>
        )}
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
                  <th className="sticky top-0 bg-[hsl(var(--muted))]/50 px-4 py-3 text-right font-medium">
                    Gap %
                  </th>
                  <th className="sticky top-0 bg-[hsl(var(--muted))]/50 px-4 py-3 font-medium">
                    Severity
                  </th>
                </tr>
              </thead>
              <tbody>
                {gaps.map((g, i) => {
                  const pct = g.demand_count > 0 ? Math.round((g.gap / g.demand_count) * 100) : 0;
                  return (
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
                      <td className="px-4 py-3 text-right tabular-nums">
                        <span
                          className={cn(
                            "font-medium",
                            pct > 50
                              ? "text-red-600 dark:text-red-400"
                              : pct > 25
                                ? "text-amber-600 dark:text-amber-400"
                                : "text-emerald-600 dark:text-emerald-400",
                          )}
                        >
                          {pct}%
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <SeverityBadge severity={g.gap_severity} />
                      </td>
                    </tr>
                  );
                })}
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
