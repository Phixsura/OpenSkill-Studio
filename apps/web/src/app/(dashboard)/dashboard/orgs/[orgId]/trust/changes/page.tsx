"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface ChangeEvent {
  id: string;
  system_id: string;
  change_type: string;
  title: string;
  impact: string;
  requires_revalidation: boolean;
  revalidation_status: string;
  created_at: string;
}

const IMPACT_COLORS: Record<string, string> = {
  none: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  low: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  high: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  requires_revalidation: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

const REVAL_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  in_progress: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  completed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  skipped: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
};

function Badge({ label, colors }: { label: string; colors: string }) {
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

export default function ChangesPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();

  const changeType = searchParams.get("change_type") || "";
  const impact = searchParams.get("impact") || "";
  const page = Number(searchParams.get("page") || "1");
  const base = `/dashboard/orgs/${orgId}/trust/changes`;

  const params = new URLSearchParams({ page: String(page), per_page: "20" });
  if (changeType) params.set("change_type", changeType);
  if (impact) params.set("impact", impact);

  const { data, isLoading } = useQuery({
    queryKey: ["trust-changes", orgId, changeType, impact, page],
    queryFn: () =>
      apiWithAuth<{ data: ChangeEvent[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/trust/changes?${params}`,
      ),
  });

  const events = data?.data ?? [];
  const total = data?.meta?.total ?? 0;
  const hasMore = data?.meta?.has_more ?? false;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Change Management</h1>

      <div className="flex flex-wrap gap-3">
        <select
          value={changeType}
          onChange={(e) => {
            const p = new URLSearchParams(searchParams);
            if (e.target.value) p.set("change_type", e.target.value);
            else p.delete("change_type");
            p.set("page", "1");
            router.push(`${base}?${p}`);
          }}
          className="rounded-md border px-3 py-1.5 text-sm bg-transparent"
        >
          <option value="">All Types</option>
          {["model_version", "provider_version", "prompt_template", "tool_permission", "component_dependency", "data_source", "evaluation_method", "intended_use", "deployment_scale", "configuration"].map(
            (v) => <option key={v} value={v}>{v.replace(/_/g, " ")}</option>,
          )}
        </select>
        <select
          value={impact}
          onChange={(e) => {
            const p = new URLSearchParams(searchParams);
            if (e.target.value) p.set("impact", e.target.value);
            else p.delete("impact");
            p.set("page", "1");
            router.push(`${base}?${p}`);
          }}
          className="rounded-md border px-3 py-1.5 text-sm bg-transparent"
        >
          <option value="">All Impacts</option>
          {["none", "low", "medium", "high", "requires_revalidation"].map(
            (v) => <option key={v} value={v}>{v.replace(/_/g, " ")}</option>,
          )}
        </select>
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {!isLoading && events.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No change events recorded.
        </div>
      )}

      {events.length > 0 && (
        <>
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Title</th>
                  <th className="px-4 py-2 font-medium">Type</th>
                  <th className="px-4 py-2 font-medium">Impact</th>
                  <th className="px-4 py-2 font-medium">Revalidation</th>
                  <th className="px-4 py-2 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {events.map((e) => (
                  <tr key={e.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                    <td className="px-4 py-2 font-medium">{e.title}</td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">{e.change_type.replace(/_/g, " ")}</td>
                    <td className="px-4 py-2"><Badge label={e.impact} colors={IMPACT_COLORS[e.impact] || ""} /></td>
                    <td className="px-4 py-2">
                      {e.requires_revalidation ? (
                        <Badge label={e.revalidation_status} colors={REVAL_COLORS[e.revalidation_status] || ""} />
                      ) : (
                        <span className="text-xs text-[hsl(var(--muted-foreground))]">—</span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">{new Date(e.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between">
            <p className="text-sm text-[hsl(var(--muted-foreground))]">{total} event{total !== 1 ? "s" : ""}</p>
            <div className="flex gap-2">
              <button disabled={page <= 1} onClick={() => { const p = new URLSearchParams(searchParams); p.set("page", String(page - 1)); router.push(`${base}?${p}`); }} className="rounded-md border px-3 py-1 text-sm disabled:opacity-50">Previous</button>
              <button disabled={!hasMore} onClick={() => { const p = new URLSearchParams(searchParams); p.set("page", String(page + 1)); router.push(`${base}?${p}`); }} className="rounded-md border px-3 py-1 text-sm disabled:opacity-50">Next</button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
