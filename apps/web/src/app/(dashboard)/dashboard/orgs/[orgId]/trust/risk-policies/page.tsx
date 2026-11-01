"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface Policy {
  id: string;
  org_id: string | null;
  name: string;
  version: number;
  is_active: boolean;
  dimensions: {
    key: string;
    label: string;
    description: string;
    weight: number;
    scale_min: number;
    scale_max: number;
    guidance: string;
  }[];
  tier_thresholds: Record<string, { max_score?: number; min_score?: number }>;
  created_by: string | null;
  created_at: string;
}

const TIER_ORDER = ["minimal", "low", "medium", "high", "critical"];

const TIER_COLORS: Record<string, string> = {
  minimal: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  low: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  high: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  critical: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export default function RiskPoliciesPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["trust-policies", orgId],
    queryFn: () => apiWithAuth<{ data: Policy[] }>(`/orgs/${orgId}/trust/risk-policies`),
  });

  const policies = data?.data ?? [];
  const activePolicy = policies.find((p) => p.is_active);

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError) {
    return <p className="text-sm text-red-600">Failed to load policies.</p>;
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Risk Scoring Policies</h1>

      {!activePolicy ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No active policy. The platform default will be used.
        </div>
      ) : (
        <div className="space-y-6">
          {/* Active Policy */}
          <div className="rounded-lg border p-6">
            <div className="flex items-baseline justify-between">
              <div>
                <h2 className="text-lg font-semibold">{activePolicy.name}</h2>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  v{activePolicy.version} · {activePolicy.org_id ? "Org-specific" : "Platform default"} ·{" "}
                  <span className="text-green-600 dark:text-green-400">Active</span>
                </p>
              </div>
            </div>

            {/* Dimensions */}
            <div className="mt-6">
              <h3 className="mb-3 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                Scoring Dimensions ({activePolicy.dimensions.length})
              </h3>
              <div className="overflow-x-auto rounded-lg border">
                <table className="w-full text-sm">
                  <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                    <tr>
                      <th className="px-4 py-2 font-medium">Dimension</th>
                      <th className="px-4 py-2 font-medium">Weight</th>
                      <th className="px-4 py-2 font-medium">Scale</th>
                      <th className="px-4 py-2 font-medium">Guidance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activePolicy.dimensions.map((dim) => (
                      <tr key={dim.key} className="border-b last:border-0">
                        <td className="px-4 py-2">
                          <p className="font-medium">{dim.label}</p>
                          <p className="text-xs text-[hsl(var(--muted-foreground))]">{dim.description}</p>
                        </td>
                        <td className="px-4 py-2 font-mono">{dim.weight}</td>
                        <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                          {dim.scale_min}–{dim.scale_max}
                        </td>
                        <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
                          {dim.guidance}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Tier Thresholds */}
            <div className="mt-6">
              <h3 className="mb-3 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                Tier Thresholds
              </h3>
              <div className="flex flex-wrap gap-3">
                {TIER_ORDER.map((tier) => {
                  const t = activePolicy.tier_thresholds[tier];
                  if (!t) return null;
                  const label = t.max_score !== undefined
                    ? `≤ ${t.max_score}`
                    : t.min_score !== undefined
                    ? `≥ ${t.min_score}`
                    : "";
                  return (
                    <div key={tier} className={`rounded-lg px-4 py-2 ${TIER_COLORS[tier]}`}>
                      <p className="text-xs font-medium uppercase">{tier}</p>
                      <p className="text-lg font-bold">{label}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Inactive Policies */}
          {policies.filter((p) => !p.is_active).length > 0 && (
            <div>
              <h3 className="mb-3 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                Previous Policies
              </h3>
              {policies
                .filter((p) => !p.is_active)
                .map((p) => (
                  <div key={p.id} className="mb-2 rounded-lg border p-4 opacity-60">
                    <p className="font-medium">{p.name}</p>
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">
                      v{p.version} · {p.dimensions.length} dimensions · Inactive
                    </p>
                  </div>
                ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
