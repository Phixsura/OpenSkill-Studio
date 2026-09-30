"use client";
/** Guardrail dashboard (ADR-017 Part D/L): events, manual incident (pauses
 * immediately), evaluate-now. Breach auto-pauses; nothing here can promote. */

import Link from "next/link";
import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EmptyState, ErrorBanner, ExperimentsNav, Pill, SectionCard } from "../../components";
import { STATUS_STYLES, fmtDate, fmtNum, type GuardrailEvent } from "../../lib";

export default function GuardrailsPage() {
  const { experimentId } = useParams<{ experimentId: string }>();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [reason, setReason] = useState("");

  const events = useQuery({
    queryKey: ["experiment-guardrail-events", experimentId],
    queryFn: () =>
      apiWithAuth<{ data: GuardrailEvent[] }>(
        `/experiments/${experimentId}/guardrails/events?limit=100`,
      ),
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["experiment-guardrail-events", experimentId] });

  const evaluateNow = useMutation({
    mutationFn: () =>
      apiWithAuth(`/experiments/${experimentId}/guardrails/evaluate`, {
        method: "POST",
        body: "{}",
      }),
    onSuccess: () => {
      setError(null);
      invalidate();
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Evaluation failed"),
  });

  const incident = useMutation({
    mutationFn: () =>
      apiWithAuth(`/experiments/${experimentId}/guardrails/incident`, {
        method: "POST",
        body: JSON.stringify({ reason: reason || null }),
      }),
    onSuccess: () => {
      setError(null);
      setReason("");
      invalidate();
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Incident report failed"),
  });

  const rows = events.data?.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <h1 className="text-xl font-semibold">
        <Link href={`/dashboard/experiments/${experimentId}`} className="hover:underline">
          Experiment
        </Link>{" "}
        · Guardrails
      </h1>
      <ErrorBanner message={error} />
      <div className="flex flex-wrap items-end gap-3">
        <button
          type="button"
          onClick={() => evaluateNow.mutate()}
          className="rounded-md border px-3 py-1.5 text-sm"
        >
          Evaluate now
        </button>
        <div className="flex items-end gap-2">
          <label className="text-xs text-slate-600">
            Incident reason
            <input
              className="block w-64 rounded-md border px-2 py-1 text-sm"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="privacy report / security event"
            />
          </label>
          <button
            type="button"
            onClick={() => incident.mutate()}
            className="rounded-md border border-rose-300 bg-rose-50 px-3 py-1.5 text-sm text-rose-800"
          >
            Report incident (pauses immediately)
          </button>
        </div>
      </div>
      <SectionCard title="Guardrail events (breach → auto-pause; SRM → alert only)">
        {rows.length === 0 ? (
          <EmptyState message="No guardrail events — clean so far." />
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="py-1 pr-3">When</th>
                <th className="py-1 pr-3">Guardrail</th>
                <th className="py-1 pr-3">Observed / threshold</th>
                <th className="py-1 pr-3">Action</th>
                <th className="py-1 pr-3">Auto</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((e) => (
                <tr key={e.id} className="border-t">
                  <td className="whitespace-nowrap py-1 pr-3 text-xs text-slate-500">
                    {fmtDate(e.created_at)}
                  </td>
                  <td className="py-1 pr-3 font-medium">{e.guardrail_key}</td>
                  <td className="py-1 pr-3">
                    {e.observed != null ? `${fmtNum(e.observed)} vs ${fmtNum(e.threshold)}` : "—"}
                  </td>
                  <td className="py-1 pr-3">
                    <Pill value={e.action} styles={STATUS_STYLES} />
                  </td>
                  <td className="py-1 pr-3">{e.auto ? "auto" : "manual"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </SectionCard>
    </div>
  );
}
