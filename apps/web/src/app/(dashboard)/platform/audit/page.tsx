"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Input } from "@/components/ui/input";
import { QueryError } from "@/components/cp-list";
import { apiWithAuth } from "@/lib/api";

interface AuditEvent {
  id: string;
  actor_user_id: string | null;
  actor_type: string;
  action: string;
  target_type: string;
  target_id: string;
  tenant_id: string | null;
  reason: string | null;
  after: Record<string, unknown> | null;
  created_at: string;
}

export default function PlatformAuditPage() {
  // R101[M35]: both free-text filters fired a request per keystroke —
  // debounce 400ms so half-typed IDs/actions don't spray requests.
  const [rawTenantId, setRawTenantId] = useState("");
  const [rawAction, setRawAction] = useState("");
  const [tenantId, setTenantId] = useState("");
  const [action, setAction] = useState("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    const t = setTimeout(() => {
      setTenantId(rawTenantId);
      setAction(rawAction);
      setPage(1);
    }, 400);
    return () => clearTimeout(t);
  }, [rawTenantId, rawAction]);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["platform-audit", tenantId, action, page],
    queryFn: () => {
      const params = new URLSearchParams({ page: String(page) });
      if (tenantId) params.set("tenant_id", tenantId);
      if (action) params.set("action", action);
      return apiWithAuth<{ data: AuditEvent[]; meta: { has_more: boolean } }>(
        `/platform/audit-events?${params.toString()}`,
      );
    },
  });
  const events = data?.data ?? [];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Input
          className="max-w-xs"
          placeholder="Tenant ID"
          value={rawTenantId}
          onChange={(e) => setRawTenantId(e.target.value)}
        />
        <Input
          className="max-w-[16rem]"
          placeholder="Action (e.g. tenant.suspended)"
          value={rawAction}
          onChange={(e) => setRawAction(e.target.value)}
        />
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
      {/* R101[M35]: query errors rendered as an empty table — an auditor
          couldn't tell "no events" from "the audit endpoint is down". */}
      {isError && <QueryError error={error} what="audit events" />}
      {!isLoading && !isError && (
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
                  <tr key={e.id} className="border-b last:border-0">
                    <td className="px-4 py-2 text-xs">{new Date(e.created_at).toLocaleString()}</td>
                    <td className="px-4 py-2 font-mono text-xs">{e.action}</td>
                    {/* R101[L16]: 10-char slices of a 26-char ULID collide and can't
                        be pasted into other tools — show the full 26 chars and keep
                        the complete id in a hover title. */}
                    <td className="px-4 py-2 text-xs">
                      {e.actor_type}
                      {e.actor_user_id ? (
                        <>
                          {" · "}
                          <span className="font-mono" title={e.actor_user_id}>
                            {e.actor_user_id.slice(0, 26)}
                          </span>
                        </>
                      ) : (
                        ""
                      )}
                    </td>
                    <td className="px-4 py-2 font-mono text-xs">
                      {e.target_type}/<span title={e.target_id}>{e.target_id.slice(0, 26)}</span>
                    </td>
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
                      {e.reason ?? (e.after ? JSON.stringify(e.after).slice(0, 80) : "—")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <button
              className="rounded-md border px-3 py-1 disabled:opacity-40"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Prev
            </button>
            <span>Page {page}</span>
            <button
              className="rounded-md border px-3 py-1 disabled:opacity-40"
              onClick={() => setPage((p) => p + 1)}
              disabled={!data?.meta?.has_more}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
