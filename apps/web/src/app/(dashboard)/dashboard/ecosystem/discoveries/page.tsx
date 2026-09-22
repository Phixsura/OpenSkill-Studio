"use client";
/** Discoveries: observation ledger + entity-resolution queue (Parts B/C). */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill } from "../components";
import { STATUS_STYLES, fmtDate } from "../lib";

interface Observation {
  id: string;
  event_type: string;
  entity_kind: string | null;
  external_ref: string | null;
  canonical_entity_id: string | null;
  observed_at: string;
  confidence: number;
  extraction_method: string;
  human_verified: boolean;
  provenance_url: string | null;
  normalized: Record<string, unknown>;
}

interface ResolutionCandidate {
  id: string;
  entity_kind: string;
  candidate_entity_id: string | null;
  match_method: string;
  confidence: number;
  status: string;
  proposed_payload: Record<string, unknown>;
}

export default function DiscoveriesPage() {
  const queryClient = useQueryClient();
  const [eventType, setEventType] = useState("");
  const [mutError, setMutError] = useState<string | null>(null);

  const observations = useQuery({
    queryKey: ["eco-observations", eventType],
    queryFn: () =>
      apiWithAuth<{ data: Observation[] }>(
        `/ecosystem/observations?limit=50${eventType ? `&event_type=${eventType}` : ""}`,
      ),
  });
  const resolutions = useQuery({
    queryKey: ["eco-resolutions"],
    queryFn: () => apiWithAuth<{ data: ResolutionCandidate[] }>("/ecosystem/resolution-candidates"),
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["eco-observations"] });
    queryClient.invalidateQueries({ queryKey: ["eco-resolutions"] });
  };

  const verify = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`/ecosystem/observations/${id}/verify`, { method: "POST" }),
    onSuccess: invalidate,
    onError: (e) => setMutError(e instanceof ApiError ? e.message : "Action failed"),
  });
  const bulkVerify = useMutation({
    mutationFn: (ids: string[]) =>
      apiWithAuth(`/ecosystem/observations/bulk-verify`, {
        method: "POST",
        body: JSON.stringify({ ids }),
      }),
    onSuccess: invalidate,
    onError: (e) => setMutError(e instanceof ApiError ? e.message : "Action failed"),
  });
  const confirm = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`/ecosystem/resolution-candidates/${id}/confirm`, {
        method: "POST",
        body: "{}",
      }),
    onSuccess: invalidate,
    onError: (e) => setMutError(e instanceof ApiError ? e.message : "Action failed"),
  });
  const llmSuggest = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`/ecosystem/resolution-candidates/${id}/llm-suggest`, { method: "POST" }),
    onSuccess: invalidate,
    onError: (e) => setMutError(e instanceof ApiError ? e.message : "Action failed"),
  });
  const reject = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`/ecosystem/resolution-candidates/${id}/reject`, { method: "POST" }),
    onSuccess: invalidate,
    onError: (e) => setMutError(e instanceof ApiError ? e.message : "Action failed"),
  });

  const pending = resolutions.data?.data ?? [];
  const rows = observations.data?.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Discoveries</h1>
      <EcosystemNav />
      {mutError && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
          {mutError}
        </div>
      )}

      <section>
        <h2 className="mb-3 text-lg font-semibold">
          Entity resolution queue{" "}
          <span className="text-sm font-normal text-[hsl(var(--muted-foreground))]">
            (low-confidence merges require your confirmation)
          </span>
        </h2>
        {pending.length === 0 ? (
          <EmptyState icon="✅" text="No resolution candidates awaiting review." />
        ) : (
          <div className="space-y-2">
            {pending.map((c) => (
              <div
                key={c.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm"
              >
                <div>
                  <div className="text-sm font-medium">
                    {String(c.proposed_payload?.name ?? "Unnamed")}{" "}
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      ({c.entity_kind})
                    </span>
                  </div>
                  <div className="text-xs text-[hsl(var(--muted-foreground))]">
                    {c.candidate_entity_id
                      ? `Merge into existing entity via ${c.match_method} (confidence ${Number(c.confidence).toFixed(2)})`
                      : "Proposes a NEW canonical entity"}
                  </div>
                </div>
                <div className="space-x-2">
                  <button
                    onClick={() => confirm.mutate(c.id)}
                    className="rounded-md bg-emerald-600 px-3 py-1 text-xs text-white"
                  >
                    Confirm
                  </button>
                  <button
                    onClick={() => reject.mutate(c.id)}
                    className="rounded-md border px-3 py-1 text-xs"
                  >
                    Reject
                  </button>
                  {!c.candidate_entity_id && (
                    <button
                      onClick={() => llmSuggest.mutate(c.id)}
                      disabled={llmSuggest.isPending}
                      className="rounded-md border px-3 py-1 text-xs disabled:opacity-50"
                      title="LLM tie-breaker — suggestion only, never auto-merges"
                    >
                      🤖 LLM suggest
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Observation ledger (append-only)</h2>
          <button
            onClick={() =>
              bulkVerify.mutate(rows.filter((o) => !o.human_verified).map((o) => o.id))
            }
            disabled={bulkVerify.isPending || rows.every((o) => o.human_verified)}
            className="rounded-md border px-3 py-1 text-xs hover:bg-[hsl(var(--secondary))] disabled:opacity-50"
          >
            Verify all shown ({rows.filter((o) => !o.human_verified).length})
          </button>
          <select
            aria-label="Filter discoveries"
            value={eventType}
            onChange={(e) => setEventType(e.target.value)}
            className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
          >
            <option value="">All events</option>
            {[
              "model_released",
              "model_deprecated",
              "price_changed",
              "api_changed",
              "limits_changed",
              "license_changed",
              "security_advisory",
              "release_published",
              "workflow_dependency_changed",
            ].map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </div>
        {rows.length === 0 ? (
          <EmptyState icon="🔭" text="No observations yet — sync a source." />
        ) : (
          <div className="overflow-x-auto rounded-lg border shadow-sm">
            <table className="w-full">
              <thead className="bg-[hsl(var(--secondary))]">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">Event</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Entity</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Method</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Observed</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Verified</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {rows.map((o) => (
                  <tr key={o.id} className="bg-[hsl(var(--card))]">
                    <td className="px-4 py-3 text-sm font-medium">{o.event_type}</td>
                    <td className="px-4 py-3 text-sm">
                      {o.external_ref ?? "—"}
                      {o.provenance_url && (
                        <a
                          href={o.provenance_url}
                          target="_blank"
                          rel="noreferrer"
                          className="ml-2 text-xs text-blue-600 underline"
                        >
                          source
                        </a>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {o.extraction_method}{" "}
                      <span className="text-xs text-[hsl(var(--muted-foreground))]">
                        ({Number(o.confidence).toFixed(2)})
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-[hsl(var(--muted-foreground))]">
                      {fmtDate(o.observed_at)}
                    </td>
                    <td className="px-4 py-3">
                      {o.human_verified ? (
                        <Pill value="confirmed" styles={STATUS_STYLES} />
                      ) : (
                        <button
                          onClick={() => verify.mutate(o.id)}
                          className="rounded-md border px-2 py-1 text-xs hover:bg-[hsl(var(--secondary))]"
                        >
                          Verify
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
