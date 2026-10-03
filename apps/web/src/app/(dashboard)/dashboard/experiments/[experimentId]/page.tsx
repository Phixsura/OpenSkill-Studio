"use client";
/** Experiment overview — lifecycle actions, ramp control, versions, audit
 * trail (ADR-017 Part L). Only legal transitions are offered; the server
 * re-validates every one (locked state machine). */

import Link from "next/link";
import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { usePlatformAdmin } from "@/lib/use-me";
import { ErrorBanner, ExperimentsNav, Pill, SectionCard } from "../components";
import {
  ALLOWED_TRANSITIONS,
  CHECKLIST_LABELS,
  ETHICS_CHECKLIST_DOMAINS,
  ETHICS_CHECKLIST_KEY,
  LAUNCH_CHECKLIST_KEYS,
  STATUS_STYLES,
  fmtDate,
  fmtPct,
  type Experiment,
} from "../lib";

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
  const isPlatformAdmin = usePlatformAdmin();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [rampPct, setRampPct] = useState("");
  // "at=ISO pct; at=ISO pct" — one step per line, e.g. "2026-10-05T09:00Z 50"
  const [planText, setPlanText] = useState("");
  const [checklist, setChecklist] = useState<Record<string, boolean>>({});
  const [startAt, setStartAt] = useState(""); // exp10: optional auto-start

  const { data } = useQuery({
    queryKey: ["experiment", experimentId],
    queryFn: () => apiWithAuth<{ data: Experiment }>(`/experiments/${experimentId}`),
  });
  const versions = useQuery({
    queryKey: ["experiment-versions", experimentId],
    queryFn: () => apiWithAuth<{ data: Version[] }>(`/experiments/${experimentId}/versions`),
  });
  const latest = useQuery({
    queryKey: ["experiment-latest-analysis", experimentId],
    queryFn: () =>
      apiWithAuth<{
        data: {
          at: string | null;
          sequential: string | null;
          look: number | null;
          result_hash: string | null;
          automated: boolean;
          primary_effects: Record<
            string,
            Record<string, { effect?: number | null; se?: number | null }>
          >;
        } | null;
      }>(`/experiments/${experimentId}/analysis/latest`),
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
        body: JSON.stringify(
          to_status === "scheduled"
            ? {
                to_status,
                checklist,
                ...(startAt ? { start_at: new Date(startAt).toISOString() } : {}),
              }
            : { to_status },
        ),
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

  const setRampPlan = useMutation({
    mutationFn: () => {
      const steps = planText
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line) => {
          const [at, pct] = line.split(/\s+/);
          return { at, ramp_bp: Math.round(Number(pct) * 100) };
        });
      return apiWithAuth(`/experiments/${experimentId}/ramp-plan`, {
        method: "PATCH",
        body: JSON.stringify({ plan: steps.length ? steps : null }),
      });
    },
    onSuccess: () => {
      setError(null);
      setPlanText("");
      invalidate();
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Ramp plan failed"),
  });

  const experiment = data?.data;
  if (!experiment) return <div className="p-6 text-sm text-slate-500">Loading…</div>;
  // promoted/rejected are OUTCOMES of a recorded decision (approver +
  // verified analysis hash) — the server refuses them on the generic
  // transition endpoint, so don't offer them as buttons here
  const nextStatuses = (ALLOWED_TRANSITIONS[experiment.status] ?? []).filter(
    (s) => s !== "promoted" && s !== "rejected",
  );
  const decisionGated = experiment.status === "analyzed";

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
          {experiment.status === "scheduled" ? (
            <div>
              <dt className="text-xs text-slate-500">Auto-starts</dt>
              <dd>
                {experiment.start_at
                  ? new Date(experiment.start_at).toLocaleString()
                  : "manual start"}
              </dd>
            </div>
          ) : null}
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
          <div>
            <dt className="text-xs text-slate-500">Guardrails checked</dt>
            <dd
              className={
                experiment.status === "running" && !experiment.last_guardrail_check_at
                  ? "text-amber-700"
                  : undefined
              }
            >
              {experiment.last_guardrail_check_at
                ? fmtDate(experiment.last_guardrail_check_at)
                : experiment.status === "running"
                  ? "never — sweep pending"
                  : "—"}
            </dd>
          </div>
        </dl>
      </SectionCard>

      <SectionCard title="Latest analysis">
        {latest.data?.data ? (
          <div className="space-y-1 text-sm">
            <div className="text-xs text-slate-500">
              {latest.data.data.at ? new Date(latest.data.data.at).toLocaleString() : "—"} ·{" "}
              {latest.data.data.sequential}
              {latest.data.data.look ? ` · look ${latest.data.data.look}` : ""}
              {latest.data.data.automated ? " · automated" : ""}
            </div>
            {Object.entries(latest.data.data.primary_effects ?? {}).map(([metric, arms]) => (
              <div key={metric}>
                <span className="font-medium">{metric}</span>
                {Object.entries(arms ?? {}).map(([arm, v]) => (
                  <span key={arm} className="ml-3 text-slate-600">
                    {arm}: {v.effect != null ? v.effect.toFixed(4) : "—"}
                    {v.se != null ? ` ±${v.se.toFixed(4)}` : ""}
                  </span>
                ))}
              </div>
            ))}
            <div className="text-xs text-slate-400">
              hash {latest.data.data.result_hash?.slice(0, 12)}…
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-500">No analysis has run yet.</p>
        )}
      </SectionCard>

      <SectionCard title="Lifecycle">
        {experiment.status === "review" ? (
          <div className="mb-3 rounded-md border border-sky-200 bg-sky-50 p-3">
            <p className="mb-2 text-xs font-medium text-sky-900">
              Launch checklist — every item must be affirmed to schedule (§5 v2)
            </p>
            {[
              ...LAUNCH_CHECKLIST_KEYS,
              ...((ETHICS_CHECKLIST_DOMAINS as readonly string[]).includes(experiment.domain)
                ? [ETHICS_CHECKLIST_KEY]
                : []),
            ].map((key) => (
              <label key={key} className="flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={Boolean(checklist[key])}
                  onChange={(e) => setChecklist({ ...checklist, [key]: e.target.checked })}
                />
                {CHECKLIST_LABELS[key] ?? key}
              </label>
            ))}
            <label className="mt-2 flex items-center gap-2 text-sm text-slate-700">
              Auto-start at
              <input
                type="datetime-local"
                aria-label="Auto-start at"
                className="rounded-md border px-2 py-1 text-xs"
                value={startAt}
                onChange={(e) => setStartAt(e.target.value)}
              />
              <span className="text-xs text-slate-500">(blank = start manually)</span>
            </label>
          </div>
        ) : null}
        <div className="flex flex-wrap items-center gap-2">
          {isPlatformAdmin ? (
            <button
              type="button"
              className="rounded-md border px-3 py-1.5 text-sm"
              onClick={async () => {
                const key = window.prompt(
                  "New experiment key for the clone (lowercase, 3-64 chars):",
                );
                if (!key) return;
                try {
                  const created = await apiWithAuth<{ data: { id: string } }>(
                    `/experiments/${experimentId}/clone`,
                    { method: "POST", body: JSON.stringify({ key }) },
                  );
                  window.location.assign(`/dashboard/experiments/${created.data.id}`);
                } catch (e) {
                  setError(e instanceof Error ? e.message : "Clone failed");
                }
              }}
            >
              Clone
            </button>
          ) : null}
          {decisionGated ? (
            <span className="mr-2 text-xs text-slate-500">
              {isPlatformAdmin
                ? "promote / reject are recorded as a decision (run the analysis, then create a decision with its result hash)"
                : "promote / reject are platform-admin decisions — share your analysis result hash with a platform admin"}
            </span>
          ) : null}
          {nextStatuses.length === 0 && !decisionGated ? (
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
        {["draft", "review", "scheduled", "running"].includes(experiment.status) ? (
          <div className="mt-3 space-y-1 text-sm">
            <div className="text-xs text-slate-500">
              Ramp plan (one step per line: ISO time, then target %; targets must increase — blank
              saves as cleared)
            </div>
            {(experiment.ramp_plan ?? []).map((step) => (
              <div key={step.at} className="text-xs text-slate-600">
                {fmtDate(step.at)} → {step.ramp_bp / 100}%
              </div>
            ))}
            <textarea
              aria-label="ramp plan steps"
              className="w-full rounded-md border px-2 py-1 font-mono text-xs"
              rows={2}
              placeholder="2026-10-05T09:00:00Z 50"
              value={planText}
              onChange={(e) => setPlanText(e.target.value)}
            />
            <button
              type="button"
              onClick={() => setRampPlan.mutate()}
              className="rounded-md border px-2 py-1 text-sm"
            >
              Save ramp plan
            </button>
          </div>
        ) : null}
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
