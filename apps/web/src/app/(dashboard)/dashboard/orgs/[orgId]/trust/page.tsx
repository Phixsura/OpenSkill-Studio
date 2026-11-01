"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface AISystem {
  id: string;
  name: string;
  slug: string;
  system_type: string;
  lifecycle: string;
  risk_tier: string | null;
  owner_user_id: string;
  version: number;
  created_at: string;
}

const RISK_COLORS: Record<string, string> = {
  minimal: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  low: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  high: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  critical: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

const LIFECYCLE_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  intake: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  under_review: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  deployed: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  monitoring: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
  paused: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  deprecated: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
  retired: "bg-gray-300 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
};

function Badge({ label, colors }: { label: string; colors: string }) {
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

function Card({ label, value, sub, alert }: { label: string; value: string; sub?: string; alert?: boolean }) {
  return (
    <div className={`rounded-lg border p-4 ${alert ? "border-amber-400" : ""}`}>
      <p className="text-xs text-[hsl(var(--muted-foreground))]">{label}</p>
      <p className="mt-1 text-xl font-bold">{value}</p>
      {sub && <p className="text-xs text-[hsl(var(--muted-foreground))]">{sub}</p>}
    </div>
  );
}

export default function TrustDashboardPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const base = `/dashboard/orgs/${orgId}/trust`;

  const { data, isLoading, isError } = useQuery({
    queryKey: ["trust-systems", orgId],
    queryFn: () =>
      apiWithAuth<{ data: AISystem[]; meta: { total: number } }>(
        `/orgs/${orgId}/trust/systems?per_page=100`,
      ),
  });

  const systems = data?.data ?? [];
  const total = data?.meta?.total ?? 0;

  // Compute stats
  const byTier: Record<string, number> = {};
  const byLifecycle: Record<string, number> = {};
  for (const s of systems) {
    const tier = s.risk_tier ?? "unassessed";
    byTier[tier] = (byTier[tier] || 0) + 1;
    byLifecycle[s.lifecycle] = (byLifecycle[s.lifecycle] || 0) + 1;
  }

  const pendingReview = systems.filter(
    (s) => s.lifecycle === "under_review" || s.lifecycle === "intake",
  ).length;

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError) {
    return <p className="text-sm text-red-600">Failed to load trust dashboard.</p>;
  }

  return (
    <div className="space-y-8">
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-bold">🛡️ Trust & Safety</h1>
        <Link
          href={`${base}/systems/new`}
          className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm text-[hsl(var(--primary-foreground))] hover:opacity-90"
        >
          Register AI System
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card label="Total AI Systems" value={String(total)} />
        <Card
          label="Pending Review"
          value={String(pendingReview)}
          alert={pendingReview > 0}
        />
        <Card
          label="High / Critical Risk"
          value={String((byTier["high"] || 0) + (byTier["critical"] || 0))}
          alert={(byTier["high"] || 0) + (byTier["critical"] || 0) > 0}
        />
        <Card
          label="Unassessed"
          value={String(byTier["unassessed"] || 0)}
          sub="Systems without risk assessment"
        />
      </div>

      {/* By Risk Tier */}
      {Object.keys(byTier).length > 0 && (
        <div>
          <h2 className="mb-3 text-lg font-semibold">By Risk Tier</h2>
          <div className="flex flex-wrap gap-3">
            {["minimal", "low", "medium", "high", "critical", "unassessed"].map((tier) =>
              byTier[tier] ? (
                <div key={tier} className="flex items-center gap-2">
                  <Badge
                    label={tier}
                    colors={RISK_COLORS[tier] || "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200"}
                  />
                  <span className="text-sm font-medium">{byTier[tier]}</span>
                </div>
              ) : null,
            )}
          </div>
        </div>
      )}

      {/* Recent Systems Table */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">AI Systems</h2>
          <Link
            href={`${base}/systems`}
            className="text-sm text-[hsl(var(--primary))] hover:underline"
          >
            View all →
          </Link>
        </div>
        {systems.length === 0 ? (
          <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
            No AI systems registered yet. Register one to start tracking trust & safety.
          </div>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Name</th>
                  <th className="px-4 py-2 font-medium">Type</th>
                  <th className="px-4 py-2 font-medium">Lifecycle</th>
                  <th className="px-4 py-2 font-medium">Risk Tier</th>
                </tr>
              </thead>
              <tbody>
                {systems.slice(0, 10).map((s) => (
                  <tr key={s.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                    <td className="px-4 py-2">
                      <Link
                        href={`${base}/systems/${s.id}`}
                        className="font-medium text-[hsl(var(--primary))] hover:underline"
                      >
                        {s.name}
                      </Link>
                    </td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                      {s.system_type.replace(/_/g, " ")}
                    </td>
                    <td className="px-4 py-2">
                      <Badge label={s.lifecycle} colors={LIFECYCLE_COLORS[s.lifecycle] || ""} />
                    </td>
                    <td className="px-4 py-2">
                      {s.risk_tier ? (
                        <Badge label={s.risk_tier} colors={RISK_COLORS[s.risk_tier] || ""} />
                      ) : (
                        <span className="text-[hsl(var(--muted-foreground))]">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Links */}
      <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-4">
        <Link href={`${base}/systems`} className="rounded-lg border p-4 hover:bg-[hsl(var(--secondary))]">
          <p className="font-medium">AI Systems</p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Manage system inventory</p>
        </Link>
        <Link href={`${base}/evidence`} className="rounded-lg border p-4 hover:bg-[hsl(var(--secondary))]">
          <p className="font-medium">Evidence</p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Assurance cases & evidence items</p>
        </Link>
        <Link href={`${base}/reviews`} className="rounded-lg border p-4 hover:bg-[hsl(var(--secondary))]">
          <p className="font-medium">Reviews</p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Human oversight review queue</p>
        </Link>
        <Link href={`${base}/guardrails`} className="rounded-lg border p-4 hover:bg-[hsl(var(--secondary))]">
          <p className="font-medium">Guardrails</p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Runtime policies & action limits</p>
        </Link>
        <Link href={`${base}/incidents`} className="rounded-lg border p-4 hover:bg-[hsl(var(--secondary))]">
          <p className="font-medium">Incidents</p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Incident lifecycle & alerts</p>
        </Link>
        <Link href={`${base}/threats`} className="rounded-lg border p-4 hover:bg-[hsl(var(--secondary))]">
          <p className="font-medium">Threats</p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Threat models & red-team testing</p>
        </Link>
        <Link href={`${base}/privacy`} className="rounded-lg border p-4 hover:bg-[hsl(var(--secondary))]">
          <p className="font-medium">Privacy</p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Data flows, consent & compliance</p>
        </Link>
        <Link href={`${base}/changes`} className="rounded-lg border p-4 hover:bg-[hsl(var(--secondary))]">
          <p className="font-medium">Changes</p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Change tracking & revalidation</p>
        </Link>
        <Link href={`${base}/risk-policies`} className="rounded-lg border p-4 hover:bg-[hsl(var(--secondary))]">
          <p className="font-medium">Risk Policies</p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Configure scoring dimensions</p>
        </Link>
        <Link href={`${base}/audit`} className="rounded-lg border p-4 hover:bg-[hsl(var(--secondary))]">
          <p className="font-medium">Audit Log</p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Trust & safety event history</p>
        </Link>
      </div>
    </div>
  );
}
