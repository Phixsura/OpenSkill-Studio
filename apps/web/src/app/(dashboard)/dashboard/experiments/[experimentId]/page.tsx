"use client";
/** Experiment overview — lifecycle actions, ramp control, versions, audit
 * trail (ADR-017 Part L). Only legal transitions are offered; the server
 * re-validates every one (locked state machine). */

import Link from "next/link";
import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { ErrorBanner, ExperimentsNav, Pill, SectionCard } from "../components";
import { ALLOWED_TRANSITIONS, STATUS_STYLES, fmtDate, fmtPct, type Experiment } from "../lib";

interface Version {
  id: string;
  version: number;
  spec: Record<string, unknown>;
  spec_hash: string;
  created_at: string;
}

interface AuditEvent {
  id: string;
  event_type: string;
  actor_user_id: string | null;
  payload: Record<string, unknown>;
  created_at: string;
}

export default function ExperimentDetailPage() {
  const { experimentId } = useParams<{ experimentId: string }>();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [rampPct, setRampPct] = useState("");

  const { data } = useQuery({
    queryKey: ["experiment", experimentId],
    queryFn: () => apiWithAuth<{ data: Experiment }>(`/experiments/${experimentId}`),
  });
  const versions = useQuery({
    queryKey: ["experiment-versions", experimentId],
    queryFn: () => apiWithAuth<{ data: Version[] }>(`/experiments/${experimentId}/versions`),
  });
  const events = useQuery({
    queryKey: ["experiment-events", experimentId],
    queryFn: () =>
      apiWithAuth<{ data: AuditEvent[] }>(`/experiments/${experimentId}/events?limit=50`),
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["experiment", experimentId] });
    queryClient.invalidateQueries({ queryKey: ["experiment-events", experimentId] });
  };

  const transition = useMutation({
    mutationFn: (to_status: string) =>
      apiWithAuth(`/experiments/${experimentId}/transition`, {
        method: "POST",
        body: JSON.stringify({ to_status }),
      }),
    onSuccess: () => {
      setError(null);
      invalidate();
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Transition failed"),
  });

  const setRamp = useMutation({
    mutationFn: () =>
      apiWithAuth(`/experiments/${experimentId}/ramp`, {
        method: "PATCH",
        body: JSON.stringify({ ramp_bp: Math.round(Number(rampPct) * 100) }),
      }),
    onSuccess: () => {
      setError(null);
      setRampPct("");
      invalidate();
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Ramp change failed"),
  });

  const experiment = data?.data;
  if (!experiment) return <div className="p-6 text-sm text-slate-500">Loading…</div>;
  const nextStatuses = ALLOWED_TRANSITIONS[experiment.status] ?? [];

  const subpages = [
    { href: "assignments", label: "Assignments" },
    { href: "metrics", label: "Metrics" },
    { href: "analysis", label: "Analysis" },
    { href: "guardrails", label: "Guardrails" },
  ];

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-xl font-semibold">{experiment.title}</h1>
        <Pill value={experiment.status} styles={STATUS_STYLES} />
        <span className="text-xs text-slate-500">{experiment.key}</span>
      </div>
      <ErrorBanner message={error} />
      <nav className="flex gap-2">
        {subpages.map((p) => (
          <Link
            key={p.href}
            href={`/dashboard/experiments/${experimentId}/${p.href}`}
            className="rounded-md border px-3 py-1 text-sm text-slate-700 hover:bg-slate-50"
          >
            {p.label}
          </Link>
        ))}
      </nav>

      <SectionCard title="Operational state">
        <dl className="grid gap-3 text-sm md:grid-cols-4">
          <div>
            <dt className="text-xs text-slate-500">Domain</dt>
            <dd>{experiment.domain}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Layer</dt>
            <dd>{experiment.layer_key}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Risk</dt>
            <dd>{experiment.risk_class}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Ramp</dt>
            <dd>{fmtPct(experiment.ramp_bp)}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Holdout</dt>
            <dd>{fmtPct(experiment.holdout_bp)}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Started</dt>
            <dd>{fmtDate(experiment.started_at)}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Ended</dt>
            <dd>{fmtDate(experiment.ended_at)}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Analysis closes</dt>
            <dd>{fmtDate(experiment.analysis_close_at)}</dd>
          </div>
        </dl>
      </SectionCard>

      <SectionCard title="Lifecycle">
        <div className="flex flex-wrap items-center gap-2">
          {nextStatuses.length === 0 ? (
            <span className="text-sm text-slate-500">Terminal status — no transitions.</span>
          ) : (
            nextStatuses.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => transition.mutate(s)}
                className="rounded-md border px-3 py-1.5 text-sm hover:bg-slate-50"
              >
                → {s}
              </button>
            ))
          )}
          {["draft", "review", "scheduled", "running"].includes(experiment.status) ? (
            <span className="ml-4 flex items-center gap-2 text-sm">
              <label htmlFor="ramp-input" className="text-xs text-slate-500">
                Ramp % (increase only while live)
              </label>
              <input
                id="ramp-input"
                className="w-20 rounded-md border px-2 py-1 text-sm"
                value={rampPct}
                onChange={(e) => setRampPct(e.target.value)}
                placeholder={String(experiment.ramp_bp / 100)}
              />
              <button
                type="button"
                onClick={() => setRamp.mutate()}
                className="rounded-md border px-2 py-1 text-sm"
              >
                Set
              </button>
            </span>
          ) : null}
        </div>
      </SectionCard>

      <SectionCard title={`Spec versions (immutable, v${experiment.current_version})`}>
        <div className="space-y-2">
          {(versions.data?.data ?? []).map((v) => (
            <details key={v.id} className="rounded-md border p-2 text-sm">
              <summary className="cursor-pointer">
                v{v.version} · <code className="text-xs">{v.spec_hash.slice(0, 12)}…</code> ·{" "}
                {fmtDate(v.created_at)}
              </summary>
              <pre className="mt-2 overflow-x-auto rounded bg-slate-50 p-2 text-xs">
                {JSON.stringify(v.spec, null, 2)}
              </pre>
            </details>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Audit trail (append-only)">
        <ul className="space-y-1 text-sm">
          {(events.data?.data ?? []).map((e) => (
            <li key={e.id} className="flex gap-3">
              <span className="whitespace-nowrap text-xs text-slate-400">
                {fmtDate(e.created_at)}
              </span>
              <span className="font-medium">{e.event_type}</span>
              <span className="truncate text-xs text-slate-500">{JSON.stringify(e.payload)}</span>
            </li>
          ))}
        </ul>
      </SectionCard>
    </div>
  );
}
