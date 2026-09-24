"use client";

import Link from "next/link";
/** Components workspace: impact, replacement candidates, drafts, rollouts (Parts I/J/K/M). */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill } from "../components";
import { SEVERITY_STYLES, STATUS_STYLES, fmtDate, shortId } from "../lib";

interface ImpactAnalysis {
  id: string;
  root_kind: string;
  root_id: string;
  classification: string;
  summary: Record<string, number | boolean>;
  deadline_at: string | null;
  computed_at: string;
  status: string;
}

interface Candidate {
  id: string;
  deprecated_kind: string;
  deprecated_id: string;
  candidate_id: string;
  score: number;
  hard_compatible: boolean;
  hard_failures: { code: string; detail: string }[];
  explanation: { factor: string; text: string }[];
  status: string;
}

interface Draft {
  id: string;
  draft_type: string;
  title: string;
  status: string;
  payload: Record<string, unknown> | null;
  validation: { valid: boolean; errors: string[] };
  published_ref: string | null;
  created_at: string;
}

interface Rollout {
  id: string;
  scope_type: string;
  status: string;
  guardrails: { min_samples?: number; thresholds?: Record<string, number> };
  comparison: Record<string, unknown> & {
    sample_size?: number;
    regressions?: string[];
  };
  created_at: string;
}

const TABS = ["Impact", "Replacements", "Drafts", "Rollouts", "Graph"] as const;

export default function ComponentsPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<(typeof TABS)[number]>("Impact");
  const [payloadOpen, setPayloadOpen] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [graphKind, setGraphKind] = useState("model_version");
  const [graphId, setGraphId] = useState("");
  const [graphNode, setGraphNode] = useState<{ kind: string; id: string } | null>(null);
  const graph = useQuery({
    queryKey: ["eco-graph-node", graphNode],
    enabled: Boolean(graphNode),
    queryFn: () =>
      apiWithAuth<{
        data: {
          depends_on: { id: string; to_kind: string; to_id: string; constraint_type: string }[];
          dependents: { id: string; from_kind: string; from_id: string; constraint_type: string }[];
        };
      }>(`/ecosystem/graph/node/${graphNode!.kind}/${graphNode!.id}`),
  });

  const impactStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      apiWithAuth(`/ecosystem/impact/analyses/${id}/status?status=${status}`, {
        method: "POST",
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["eco-impact"] }),
    onError: (e) => setError(e instanceof ApiError ? e.message : "Status change failed"),
  });
  const impact = useQuery({
    queryKey: ["eco-impact"],
    queryFn: () => apiWithAuth<{ data: ImpactAnalysis[] }>("/ecosystem/impact/analyses"),
  });
  const candidates = useQuery({
    queryKey: ["eco-candidates"],
    queryFn: () => apiWithAuth<{ data: Candidate[] }>("/ecosystem/replacements/candidates"),
  });
  const drafts = useQuery({
    queryKey: ["eco-drafts"],
    queryFn: () => apiWithAuth<{ data: Draft[] }>("/ecosystem/drafts"),
  });
  const rollouts = useQuery({
    queryKey: ["eco-rollouts"],
    queryFn: () => apiWithAuth<{ data: Rollout[] }>("/ecosystem/rollouts"),
  });

  const invalidateAll = () => {
    for (const key of ["eco-impact", "eco-candidates", "eco-drafts", "eco-rollouts"]) {
      queryClient.invalidateQueries({ queryKey: [key] });
    }
  };
  const onError = (e: unknown) => setError(e instanceof ApiError ? e.message : "Action failed");

  const decideCandidate = useMutation({
    mutationFn: ({ id, decision }: { id: string; decision: string }) =>
      apiWithAuth(`/ecosystem/replacements/candidates/${id}/decide`, {
        method: "POST",
        body: JSON.stringify({ decision }),
      }),
    onSuccess: () => {
      setError(null);
      invalidateAll();
    },
    onError,
  });
  const draftAction = useMutation({
    mutationFn: ({ id, action }: { id: string; action: string }) =>
      apiWithAuth(`/ecosystem/drafts/${id}/${action}`, { method: "POST" }),
    onSuccess: () => {
      setError(null);
      invalidateAll();
    },
    onError,
  });
  const rolloutAction = useMutation({
    mutationFn: ({ id, action, decision }: { id: string; action: string; decision?: string }) =>
      apiWithAuth(`/ecosystem/rollouts/${id}/${action}`, {
        method: "POST",
        body: decision ? JSON.stringify({ decision }) : undefined,
      }),
    onSuccess: () => {
      setError(null);
      invalidateAll();
    },
    onError,
  });

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Component Lifecycle</h1>
      <EcosystemNav />
      <div className="flex gap-2">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-md px-3 py-1.5 text-sm ${
              tab === t
                ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                : "bg-[hsl(var(--secondary))]"
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {tab === "Impact" &&
        ((impact.data?.data ?? []).length === 0 ? (
          <EmptyState icon="🎯" text="No impact analyses yet." />
        ) : (
          <div className="space-y-2">
            {(impact.data?.data ?? []).map((a) => (
              <div key={a.id} className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <Pill value={a.classification} styles={SEVERITY_STYLES} />
                  <span className="text-sm font-medium">
                    {a.root_kind} {shortId(a.root_id)}
                  </span>
                  <Link
                    href={`/dashboard/ecosystem/changes?entity=${a.root_id}`}
                    className="text-xs text-blue-600 underline"
                  >
                    changes
                  </Link>
                  <Pill value={a.status} styles={STATUS_STYLES} />
                  {a.deadline_at && (
                    <span className="text-xs text-orange-700">
                      deadline {fmtDate(a.deadline_at)}
                    </span>
                  )}
                  {a.status === "open" && (
                    <>
                      <button
                        onClick={() => impactStatus.mutate({ id: a.id, status: "acknowledged" })}
                        className="rounded-md border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
                      >
                        Acknowledge
                      </button>
                      <button
                        onClick={() => impactStatus.mutate({ id: a.id, status: "resolved" })}
                        className="rounded-md border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
                      >
                        Resolve
                      </button>
                    </>
                  )}
                  {a.status === "acknowledged" && (
                    <button
                      onClick={() => impactStatus.mutate({ id: a.id, status: "resolved" })}
                      className="rounded-md border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
                    >
                      Resolve
                    </button>
                  )}
                </div>
                <div className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
                  Affected:{" "}
                  {Object.entries(a.summary)
                    .filter(([k, v]) => k !== "truncated" && typeof v === "number")
                    .map(([k, v]) => `${k} × ${v}`)
                    .join(", ") || "nothing"}
                  {a.summary.truncated === true && " (truncated)"}
                </div>
              </div>
            ))}
          </div>
        ))}

      {tab === "Replacements" &&
        ((candidates.data?.data ?? []).length === 0 ? (
          <EmptyState icon="🔁" text="No replacement candidates yet." />
        ) : (
          <div className="space-y-2">
            {(candidates.data?.data ?? []).map((c) => (
              <div key={c.id} className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="text-sm font-medium">
                    {shortId(c.deprecated_id)} → {shortId(c.candidate_id)}{" "}
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      score {Number(c.score).toFixed(3)}
                    </span>{" "}
                    <Pill value={c.status} styles={STATUS_STYLES} />
                    {!c.hard_compatible && (
                      <span className="ml-2 rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-700">
                        hard incompatible — never approvable
                      </span>
                    )}
                  </div>
                  {c.status === "proposed" && c.hard_compatible && (
                    <div className="space-x-2">
                      <button
                        onClick={() => decideCandidate.mutate({ id: c.id, decision: "approve" })}
                        className="rounded-md bg-emerald-600 px-3 py-1 text-xs text-white"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => decideCandidate.mutate({ id: c.id, decision: "reject" })}
                        className="rounded-md border px-3 py-1 text-xs"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
                <ul className="mt-2 space-y-0.5 text-xs text-[hsl(var(--muted-foreground))]">
                  {(c.hard_failures ?? []).map((f, i) => (
                    <li key={i} className="text-red-600">
                      ✗ {f.code}: {f.detail}
                    </li>
                  ))}
                  {(c.explanation ?? []).map((line, i) => (
                    <li key={i}>• {line.text}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ))}

      {tab === "Drafts" &&
        ((drafts.data?.data ?? []).length === 0 ? (
          <EmptyState
            icon="📝"
            text="No component drafts. External discoveries generate drafts only — never auto-published."
          />
        ) : (
          <div className="space-y-2">
            {(drafts.data?.data ?? []).map((d) => (
              <div
                key={d.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm"
              >
                <div>
                  <div className="text-sm font-medium">
                    {d.title}{" "}
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      ({d.draft_type})
                    </span>
                  </div>
                  <div className="mt-1 flex items-center gap-2 text-xs">
                    <Pill value={d.status} styles={STATUS_STYLES} />
                    {!d.validation?.valid && (
                      <span className="text-red-600">
                        invalid: {(d.validation?.errors ?? []).join("; ")}
                      </span>
                    )}
                    {d.published_ref && (
                      <span className="text-[hsl(var(--muted-foreground))]">
                        → {shortId(d.published_ref)}
                      </span>
                    )}
                  </div>
                </div>
                <div className="space-x-2">
                  <button
                    onClick={() => setPayloadOpen(payloadOpen === d.id ? null : d.id)}
                    className="rounded-md border px-3 py-1 text-xs"
                  >
                    {payloadOpen === d.id ? "Hide payload" : "Review payload"}
                  </button>
                  {d.status === "draft" && (
                    <button
                      onClick={() => draftAction.mutate({ id: d.id, action: "submit-review" })}
                      className="rounded-md border px-3 py-1 text-xs"
                    >
                      Submit for review
                    </button>
                  )}
                  {d.status === "in_review" && (
                    <>
                      <button
                        onClick={() => draftAction.mutate({ id: d.id, action: "approve" })}
                        className="rounded-md bg-emerald-600 px-3 py-1 text-xs text-white"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => draftAction.mutate({ id: d.id, action: "reject" })}
                        className="rounded-md border px-3 py-1 text-xs"
                      >
                        Reject
                      </button>
                    </>
                  )}
                  {d.status === "approved" && (
                    <button
                      onClick={() => draftAction.mutate({ id: d.id, action: "publish" })}
                      className="rounded-md bg-[hsl(var(--primary))] px-3 py-1 text-xs text-[hsl(var(--primary-foreground))]"
                    >
                      Publish
                    </button>
                  )}
                </div>
                {payloadOpen === d.id && (
                  <pre className="mt-2 w-full overflow-x-auto rounded-md border bg-[hsl(var(--background))] p-3 font-mono text-xs">
                    {JSON.stringify(d.payload ?? {}, null, 2)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        ))}

      {tab === "Rollouts" &&
        ((rollouts.data?.data ?? []).length === 0 ? (
          <EmptyState
            icon="🚦"
            text="No rollout plans. Replacements roll out through explicit canary validation."
          />
        ) : (
          <div className="space-y-2">
            {(rollouts.data?.data ?? []).map((r) => (
              <div key={r.id} className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="text-sm font-medium">
                    {r.scope_type.replaceAll("_", " ")}{" "}
                    <Pill value={r.status} styles={STATUS_STYLES} />
                  </div>
                  <div className="space-x-2">
                    {r.status === "draft" && (
                      <button
                        onClick={() => rolloutAction.mutate({ id: r.id, action: "start" })}
                        className="rounded-md border px-3 py-1 text-xs"
                      >
                        Start
                      </button>
                    )}
                    {r.status === "running" && (
                      <button
                        onClick={() => rolloutAction.mutate({ id: r.id, action: "evaluate" })}
                        className="rounded-md border px-3 py-1 text-xs"
                      >
                        Evaluate
                      </button>
                    )}
                    {r.status === "evaluating" && (
                      <>
                        <button
                          onClick={() =>
                            rolloutAction.mutate({
                              id: r.id,
                              action: "decide",
                              decision: "promote",
                            })
                          }
                          className="rounded-md bg-emerald-600 px-3 py-1 text-xs text-white"
                        >
                          Promote
                        </button>
                        <button
                          onClick={() =>
                            rolloutAction.mutate({ id: r.id, action: "decide", decision: "reject" })
                          }
                          className="rounded-md border px-3 py-1 text-xs"
                        >
                          Reject
                        </button>
                      </>
                    )}
                  </div>
                </div>
                {(r.comparison?.regressions ?? []).length > 0 && (
                  <div className="mt-2 rounded-md border border-red-300 bg-red-50 px-3 py-1 text-xs text-red-700">
                    Guarded regression: {(r.comparison.regressions ?? []).join(", ")} — promote
                    blocked
                  </div>
                )}
                {r.comparison?.sample_size != null &&
                  (r.guardrails?.min_samples ?? 0) > (r.comparison.sample_size ?? 0) && (
                    <div className="mt-2 rounded-md border border-amber-300 bg-amber-50 px-3 py-1 text-xs text-amber-800">
                      Samples {r.comparison.sample_size}/{r.guardrails.min_samples} — below
                      guardrail
                    </div>
                  )}
                {Object.keys(r.comparison ?? {}).length > 0 && (
                  <div className="mt-2 grid gap-1 text-xs md:grid-cols-2">
                    {Object.entries(r.comparison)
                      .filter(
                        ([, cmp]) =>
                          typeof cmp === "object" && cmp !== null && "delta" in (cmp as object),
                      )
                      .map(([dim, cmp]) => {
                        const c = cmp as {
                          baseline: number;
                          candidate: number;
                          improved: boolean;
                          p_value?: number;
                          significant?: boolean;
                        };
                        return (
                          <div
                            key={dim}
                            className={c.improved ? "text-emerald-700" : "text-red-600"}
                          >
                            {dim}: {c.baseline} → {c.candidate} {c.improved ? "▲" : "▼"}
                            {c.p_value != null && (
                              <span className="ml-1 text-[hsl(var(--muted-foreground))]">
                                p={c.p_value}
                                {c.significant ? "*" : " (ns)"}
                              </span>
                            )}
                          </div>
                        );
                      })}
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
      {tab === "Graph" && (
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <select
              aria-label="Filter"
              value={graphKind}
              onChange={(e) => setGraphKind(e.target.value)}
              className="rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-sm"
            >
              {[
                "model_version",
                "model",
                "provider",
                "tool",
                "node_package",
                "workflow_pack",
                "workflow_pack_release",
                "skill_pack",
                "learning_path",
                "capability",
              ].map((k) => (
                <option key={k}>{k}</option>
              ))}
            </select>
            <input
              placeholder="node id"
              value={graphId}
              onChange={(e) => setGraphId(e.target.value)}
              className="w-72 rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-sm"
            />
            <button
              onClick={() => graphId && setGraphNode({ kind: graphKind, id: graphId })}
              className="rounded-md bg-[hsl(var(--primary))] px-3 py-1 text-sm text-[hsl(var(--primary-foreground))]"
            >
              Inspect node
            </button>
          </div>
          {graphNode && graph.data?.data && (
            <svg
              viewBox="0 0 900 360"
              className="w-full rounded-lg border bg-[hsl(var(--card))] shadow-sm"
              role="img"
              aria-label="Dependency graph"
            >
              {(() => {
                const deps = graph.data.data.depends_on.slice(0, 8);
                const dents = graph.data.data.dependents.slice(0, 8);
                const yFor = (i: number, n: number) =>
                  n <= 1 ? 180 : 40 + (i * 300) / Math.max(n - 1, 1);
                const short = (k: string, id: string) => `${k}:${id.slice(0, 8)}…`;
                return (
                  <g fontSize="11" fontFamily="ui-monospace, monospace">
                    {deps.map((e, i) => (
                      <g key={e.id}>
                        <line
                          x1={230}
                          y1={yFor(i, deps.length)}
                          x2={430}
                          y2={180}
                          stroke="currentColor"
                          strokeOpacity="0.35"
                        />
                        <rect
                          x={20}
                          y={yFor(i, deps.length) - 14}
                          width={210}
                          height={28}
                          rx={6}
                          fill="hsl(210 40% 96%)"
                          stroke="currentColor"
                          strokeOpacity="0.25"
                        />
                        <text x={30} y={yFor(i, deps.length) + 4}>
                          {short(e.to_kind, e.to_id)}
                        </text>
                      </g>
                    ))}
                    {dents.map((e, i) => (
                      <g key={e.id}>
                        <line
                          x1={470}
                          y1={180}
                          x2={670}
                          y2={yFor(i, dents.length)}
                          stroke="currentColor"
                          strokeOpacity="0.35"
                        />
                        <rect
                          x={670}
                          y={yFor(i, dents.length) - 14}
                          width={210}
                          height={28}
                          rx={6}
                          fill="hsl(38 92% 95%)"
                          stroke="currentColor"
                          strokeOpacity="0.25"
                        />
                        <text x={680} y={yFor(i, dents.length) + 4}>
                          {short(e.from_kind, e.from_id)}
                        </text>
                      </g>
                    ))}
                    <rect
                      x={330}
                      y={162}
                      width={240}
                      height={36}
                      rx={8}
                      fill="hsl(222 47% 90%)"
                      stroke="currentColor"
                      strokeOpacity="0.5"
                    />
                    <text x={342} y={184} fontWeight="bold">
                      {short(graphNode.kind, graphNode.id)}
                    </text>
                    <text x={20} y={352} fontSize="10" opacity="0.6">
                      ← depends on ({graph.data.data.depends_on.length}) · dependents (
                      {graph.data.data.dependents.length}) →
                    </text>
                  </g>
                );
              })()}
            </svg>
          )}
          {graphNode && graph.data?.data ? (
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
                <h3 className="mb-2 text-sm font-semibold">
                  Depends on ({graph.data.data.depends_on.length})
                </h3>
                {graph.data.data.depends_on.map((e) => (
                  <button
                    key={e.id}
                    onClick={() => setGraphNode({ kind: e.to_kind, id: e.to_id })}
                    className="block w-full rounded px-2 py-1 text-left text-xs hover:bg-[hsl(var(--secondary))]"
                  >
                    → {e.to_kind}:{e.to_id.slice(0, 12)}…{" "}
                    <span className="text-[hsl(var(--muted-foreground))]">
                      ({e.constraint_type})
                    </span>
                  </button>
                ))}
              </div>
              <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
                <h3 className="mb-2 text-sm font-semibold">
                  Dependents ({graph.data.data.dependents.length})
                </h3>
                {graph.data.data.dependents.map((e) => (
                  <button
                    key={e.id}
                    onClick={() => setGraphNode({ kind: e.from_kind, id: e.from_id })}
                    className="block w-full rounded px-2 py-1 text-left text-xs hover:bg-[hsl(var(--secondary))]"
                  >
                    ← {e.from_kind}:{e.from_id.slice(0, 12)}…{" "}
                    <span className="text-[hsl(var(--muted-foreground))]">
                      ({e.constraint_type})
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <EmptyState icon="🕸️" text="Enter a node to walk the dependency graph both ways." />
          )}
        </div>
      )}
    </div>
  );
}
