"use client";
/** Typed change feed with severity filter + acknowledge (Part B). */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill } from "../components";
import { SEVERITY_STYLES, fmtDate } from "../lib";

interface ChangeEvent {
  id: string;
  change_type: string;
  field: string;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  severity: string;
  entity_kind: string | null;
  detected_at: string;
  acknowledged: boolean;
}

const SEVERITIES = [
  "info",
  "update_available",
  "degraded",
  "breaking",
  "security_critical",
  "sunset_risk",
];

export default function ChangesPage() {
  const queryClient = useQueryClient();
  const [severity, setSeverity] = useState("");
  const [mutError, setMutError] = useState<string | null>(null);
  const [showAcked, setShowAcked] = useState(false);
  const [pages, setPages] = useState<ChangeEvent[][]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);

  const filterKey = `${severity}|${showAcked}`;
  const { data, isLoading } = useQuery({
    queryKey: ["eco-changes", filterKey],
    queryFn: async () => {
      const res = await apiWithAuth<{
        data: ChangeEvent[];
        meta: { has_more: boolean; next_cursor: string | null };
      }>(
        `/ecosystem/changes?limit=50${severity ? `&severity=${severity}` : ""}${
          showAcked ? "" : "&acknowledged=false"
        }`,
      );
      setPages([res.data]);
      setCursor(res.meta?.next_cursor ?? null);
      setHasMore(Boolean(res.meta?.has_more));
      return res;
    },
  });

  const loadMore = async () => {
    if (!cursor) return;
    const res = await apiWithAuth<{
      data: ChangeEvent[];
      meta: { has_more: boolean; next_cursor: string | null };
    }>(
      `/ecosystem/changes?limit=50&cursor=${cursor}${
        severity ? `&severity=${severity}` : ""
      }${showAcked ? "" : "&acknowledged=false"}`,
    );
    setPages((prev) => [...prev, res.data]);
    setCursor(res.meta?.next_cursor ?? null);
    setHasMore(Boolean(res.meta?.has_more));
  };

  const acknowledge = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`/ecosystem/changes/${id}/acknowledge`, { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["eco-changes"] }),
    onError: (e) => setMutError(e instanceof ApiError ? e.message : "Action failed"),
  });

  const rows = pages.length > 0 ? pages.flat() : (data?.data ?? []);

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Change Feed</h1>
      <EcosystemNav />
      {mutError && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
          {mutError}
        </div>
      )}
      <div className="flex flex-wrap items-center gap-3">
        <select
          aria-label="Filter by severity"
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
        >
          <option value="">All severities</option>
          {SEVERITIES.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={showAcked}
            onChange={(e) => setShowAcked(e.target.checked)}
          />
          Include acknowledged
        </label>
      </div>
      {isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading changes…</div>
      ) : rows.length === 0 ? (
        <EmptyState icon="📭" text="No changes match this filter." />
      ) : (
        <div className="space-y-2">
          {rows.map((c) => (
            <div
              key={c.id}
              className="flex flex-wrap items-start justify-between gap-3 rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <Pill value={c.severity} styles={SEVERITY_STYLES} />
                  <span className="text-sm font-medium">
                    {c.change_type} · {c.field}
                  </span>
                  {c.entity_kind && (
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      ({c.entity_kind})
                    </span>
                  )}
                </div>
                <div className="mt-1 font-mono text-xs text-[hsl(var(--muted-foreground))]">
                  {c.old_value ? JSON.stringify(c.old_value) : "∅"} →{" "}
                  {c.new_value ? JSON.stringify(c.new_value) : "∅"}
                </div>
                <div className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                  {fmtDate(c.detected_at)}
                </div>
              </div>
              {!c.acknowledged && (
                <button
                  onClick={() => acknowledge.mutate(c.id)}
                  className="rounded-md border px-3 py-1 text-xs hover:bg-[hsl(var(--secondary))]"
                >
                  Acknowledge
                </button>
              )}
            </div>
          ))}
          {hasMore && (
            <button
              onClick={loadMore}
              className="w-full rounded-md border px-3 py-2 text-sm hover:bg-[hsl(var(--secondary))]"
            >
              Load more (cursor)
            </button>
          )}
        </div>
      )}
    </div>
  );
}
