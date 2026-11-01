"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
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

export default function SystemsListPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const base = `/dashboard/orgs/${orgId}/trust`;

  const lifecycle = searchParams.get("lifecycle") || "";
  const systemType = searchParams.get("system_type") || "";
  const riskTier = searchParams.get("risk_tier") || "";
  const page = Number(searchParams.get("page") || "1");

  const params = new URLSearchParams();
  params.set("page", String(page));
  params.set("per_page", "20");
  if (lifecycle) params.set("lifecycle", lifecycle);
  if (systemType) params.set("system_type", systemType);
  if (riskTier) params.set("risk_tier", riskTier);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["trust-systems", orgId, lifecycle, systemType, riskTier, page],
    queryFn: () =>
      apiWithAuth<{ data: AISystem[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/trust/systems?${params}`,
      ),
  });

  const systems = data?.data ?? [];
  const total = data?.meta?.total ?? 0;
  const hasMore = data?.meta?.has_more ?? false;

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-bold">AI Systems</h1>
        <Link
          href={`${base}/systems/new`}
          className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm text-[hsl(var(--primary-foreground))] hover:opacity-90"
        >
          Register System
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select
          value={lifecycle}
          onChange={(e) => {
            const p = new URLSearchParams(searchParams);
            if (e.target.value) p.set("lifecycle", e.target.value);
            else p.delete("lifecycle");
            p.set("page", "1");
            router.push(`${base}/systems?${p}`);
          }}
          className="rounded-md border px-3 py-1.5 text-sm bg-transparent"
        >
          <option value="">All Lifecycles</option>
          {["draft", "intake", "under_review", "approved", "deployed", "monitoring", "paused", "deprecated", "retired"].map(
            (v) => <option key={v} value={v}>{v.replace(/_/g, " ")}</option>,
          )}
        </select>
        <select
          value={systemType}
          onChange={(e) => {
            const p = new URLSearchParams(searchParams);
            if (e.target.value) p.set("system_type", e.target.value);
            else p.delete("system_type");
            p.set("page", "1");
            router.push(`${base}/systems?${p}`);
          }}
          className="rounded-md border px-3 py-1.5 text-sm bg-transparent"
        >
          <option value="">All Types</option>
          {["workflow_pack", "developer_app", "provider_binding", "evaluation_pipeline", "skill_pack", "custom"].map(
            (v) => <option key={v} value={v}>{v.replace(/_/g, " ")}</option>,
          )}
        </select>
        <select
          value={riskTier}
          onChange={(e) => {
            const p = new URLSearchParams(searchParams);
            if (e.target.value) p.set("risk_tier", e.target.value);
            else p.delete("risk_tier");
            p.set("page", "1");
            router.push(`${base}/systems?${p}`);
          }}
          className="rounded-md border px-3 py-1.5 text-sm bg-transparent"
        >
          <option value="">All Risk Tiers</option>
          {["minimal", "low", "medium", "high", "critical"].map(
            (v) => <option key={v} value={v}>{v}</option>,
          )}
        </select>
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
      {isError && <p className="text-sm text-red-600">Failed to load systems.</p>}

      {!isLoading && systems.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No AI systems found. Adjust filters or register a new system.
        </div>
      )}

      {systems.length > 0 && (
        <>
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Name</th>
                  <th className="px-4 py-2 font-medium">Type</th>
                  <th className="px-4 py-2 font-medium">Lifecycle</th>
                  <th className="px-4 py-2 font-medium">Risk Tier</th>
                  <th className="px-4 py-2 font-medium">Version</th>
                  <th className="px-4 py-2 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {systems.map((s) => (
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
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">v{s.version}</td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                      {new Date(s.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-[hsl(var(--muted-foreground))]">{total} system{total !== 1 ? "s" : ""}</p>
            <div className="flex gap-2">
              <button
                disabled={page <= 1}
                onClick={() => {
                  const p = new URLSearchParams(searchParams);
                  p.set("page", String(page - 1));
                  router.push(`${base}/systems?${p}`);
                }}
                className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <button
                disabled={!hasMore}
                onClick={() => {
                  const p = new URLSearchParams(searchParams);
                  p.set("page", String(page + 1));
                  router.push(`${base}/systems?${p}`);
                }}
                className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
