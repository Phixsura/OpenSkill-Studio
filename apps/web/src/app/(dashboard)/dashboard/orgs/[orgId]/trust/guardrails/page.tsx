"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface Guardrail {
  id: string;
  name: string;
  guardrail_type: string;
  status: string;
  is_blocking: boolean;
  priority: number;
  system_id: string | null;
  created_at: string;
}

interface Boundary {
  id: string;
  name: string;
  boundary_type: string;
  limit_value: number;
  limit_period: string | null;
  current_usage: number;
  is_active: boolean;
  system_id: string | null;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  disabled: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

function Badge({ label, colors }: { label: string; colors: string }) {
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

function UsageBar({ current, limit }: { current: number; limit: number }) {
  const pct = Math.min((current / limit) * 100, 100);
  const color = pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-24 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-[hsl(var(--muted-foreground))]">
        {current}/{limit}
      </span>
    </div>
  );
}

export default function GuardrailsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = (searchParams.get("tab") as "guardrails" | "boundaries") || "guardrails";

  const { data: guardrailData, isLoading: gLoading } = useQuery({
    queryKey: ["trust-guardrails", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Guardrail[]; meta: { total: number } }>(
        `/orgs/${orgId}/trust/guardrails?per_page=50`,
      ),
    enabled: tab === "guardrails",
  });

  const { data: boundaryData, isLoading: bLoading } = useQuery({
    queryKey: ["trust-boundaries", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Boundary[]; meta: { total: number } }>(
        `/orgs/${orgId}/trust/boundaries?per_page=50`,
      ),
    enabled: tab === "boundaries",
  });

  const guardrails = guardrailData?.data ?? [];
  const boundaries = boundaryData?.data ?? [];
  const isLoading = tab === "guardrails" ? gLoading : bLoading;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Runtime Guardrails</h1>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {(["guardrails", "boundaries"] as const).map((t) => (
          <button
            key={t}
            onClick={() => {
              const p = new URLSearchParams(searchParams);
              p.set("tab", t);
              router.push(`/dashboard/orgs/${orgId}/trust/guardrails?${p}`);
            }}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              tab === t
                ? "border-[hsl(var(--primary))] text-[hsl(var(--primary))]"
                : "border-transparent text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
            }`}
          >
            {t === "guardrails" ? "Guardrail Policies" : "Action Boundaries"}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {/* Guardrails Tab */}
      {tab === "guardrails" && !isLoading && (
        <>
          {guardrails.length === 0 ? (
            <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
              No guardrail policies configured.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                  <tr>
                    <th className="px-4 py-2 font-medium">Name</th>
                    <th className="px-4 py-2 font-medium">Type</th>
                    <th className="px-4 py-2 font-medium">Status</th>
                    <th className="px-4 py-2 font-medium">Mode</th>
                    <th className="px-4 py-2 font-medium">Priority</th>
                    <th className="px-4 py-2 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {guardrails.map((g) => (
                    <tr key={g.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                      <td className="px-4 py-2 font-medium">{g.name}</td>
                      <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                        {g.guardrail_type.replace(/_/g, " ")}
                      </td>
                      <td className="px-4 py-2">
                        <Badge label={g.status} colors={STATUS_COLORS[g.status] || ""} />
                      </td>
                      <td className="px-4 py-2">
                        <span className={`text-xs ${g.is_blocking ? "text-red-600 dark:text-red-400" : "text-[hsl(var(--muted-foreground))]"}`}>
                          {g.is_blocking ? "Blocking" : "Shadow"}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">{g.priority}</td>
                      <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                        {new Date(g.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* Boundaries Tab */}
      {tab === "boundaries" && !isLoading && (
        <>
          {boundaries.length === 0 ? (
            <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
              No action boundaries configured.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                  <tr>
                    <th className="px-4 py-2 font-medium">Name</th>
                    <th className="px-4 py-2 font-medium">Type</th>
                    <th className="px-4 py-2 font-medium">Usage</th>
                    <th className="px-4 py-2 font-medium">Period</th>
                    <th className="px-4 py-2 font-medium">Active</th>
                  </tr>
                </thead>
                <tbody>
                  {boundaries.map((b) => (
                    <tr key={b.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                      <td className="px-4 py-2 font-medium">{b.name}</td>
                      <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                        {b.boundary_type.replace(/_/g, " ")}
                      </td>
                      <td className="px-4 py-2">
                        <UsageBar current={b.current_usage} limit={b.limit_value} />
                      </td>
                      <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                        {b.limit_period ? `per ${b.limit_period}` : "absolute"}
                      </td>
                      <td className="px-4 py-2">
                        <span className={b.is_active ? "text-green-600 dark:text-green-400" : "text-[hsl(var(--muted-foreground))]"}>
                          {b.is_active ? "Yes" : "No"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
