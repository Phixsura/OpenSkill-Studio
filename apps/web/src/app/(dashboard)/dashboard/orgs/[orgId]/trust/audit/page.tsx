"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface AuditEvent {
  id: string;
  org_id: string;
  actor_user_id: string | null;
  actor_type: string;
  action: string;
  target_type: string;
  target_id: string;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
  reason: string | null;
  created_at: string;
}

export default function TrustAuditPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const base = `/dashboard/orgs/${orgId}/trust`;

  const action = searchParams.get("action") || "";
  const page = Number(searchParams.get("page") || "1");

  const params = new URLSearchParams();
  params.set("page", String(page));
  params.set("per_page", "20");
  if (action) params.set("action", action);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["trust-audit", orgId, action, page],
    queryFn: () =>
      apiWithAuth<{ data: AuditEvent[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/trust/audit-log?${params}`,
      ),
  });

  const events = data?.data ?? [];
  const total = data?.meta?.total ?? 0;
  const hasMore = data?.meta?.has_more ?? false;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Trust Audit Log</h1>

      {/* Filter */}
      <div className="flex gap-3">
        <input
          type="text"
          value={action}
          onChange={(e) => {
            const p = new URLSearchParams(searchParams);
            if (e.target.value) p.set("action", e.target.value);
            else p.delete("action");
            p.set("page", "1");
            router.push(`${base}/audit?${p}`);
          }}
          placeholder="Filter by action (e.g. system.created)"
          className="rounded-md border px-3 py-1.5 text-sm bg-transparent flex-1 max-w-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
        />
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
      {isError && <p className="text-sm text-red-600">Failed to load audit log.</p>}

      {!isLoading && events.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No audit events found.
        </div>
      )}

      {events.length > 0 && (
        <>
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">When</th>
                  <th className="px-4 py-2 font-medium">Action</th>
                  <th className="px-4 py-2 font-medium">Actor</th>
                  <th className="px-4 py-2 font-medium">Target</th>
                  <th className="px-4 py-2 font-medium">Detail</th>
                </tr>
              </thead>
              <tbody>
                {events.map((e) => (
                  <tr key={e.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))] whitespace-nowrap">
                      {new Date(e.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-2">
                      <code className="rounded bg-[hsl(var(--secondary))] px-1.5 py-0.5 text-xs">
                        {e.action}
                      </code>
                    </td>
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
                      {e.actor_type}
                      {e.actor_user_id && (
                        <span className="ml-1 font-mono text-[10px]">{e.actor_user_id.slice(0, 8)}…</span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-xs">
                      {e.target_type}{" "}
                      <span className="font-mono text-[10px] text-[hsl(var(--muted-foreground))]">
                        {e.target_id.slice(0, 8)}…
                      </span>
                    </td>
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
                      {e.reason && <span className="italic">{e.reason}</span>}
                      {e.after && !e.reason && (
                        <span className="font-mono">
                          {Object.entries(e.after)
                            .slice(0, 3)
                            .map(([k, v]) => `${k}=${String(v)}`)
                            .join(", ")}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between">
            <p className="text-sm text-[hsl(var(--muted-foreground))]">{total} event{total !== 1 ? "s" : ""}</p>
            <div className="flex gap-2">
              <button
                disabled={page <= 1}
                onClick={() => {
                  const p = new URLSearchParams(searchParams);
                  p.set("page", String(page - 1));
                  router.push(`${base}/audit?${p}`);
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
                  router.push(`${base}/audit?${p}`);
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
