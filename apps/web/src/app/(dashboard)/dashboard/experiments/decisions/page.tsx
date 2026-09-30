"use client";
/** Decision registry — searchable organizational memory (ADR-017 Part J).
 * Filters are shareable URL state; the meta strip shows corpus aggregates. */

import Link from "next/link";
import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiWithAuth } from "@/lib/api";
import { EmptyState, ExperimentsNav, Pill, SectionCard } from "../components";
import { DECISIONS, EXPERIMENT_DOMAINS, fmtDate, type DecisionRecord } from "../lib";

const DECISION_STYLES: Record<string, string> = {
  promote: "bg-green-100 text-green-800",
  reject: "bg-rose-100 text-rose-800",
  inconclusive: "bg-slate-100 text-slate-700",
  extend: "bg-sky-100 text-sky-800",
};

export default function DecisionsPage() {
  return (
    <Suspense>
      <DecisionsInner />
    </Suspense>
  );
}

function DecisionsInner() {
  const router = useRouter();
  const params = useSearchParams();
  const [domain, setDomainState] = useState(params.get("domain") ?? "");
  const [decision, setDecisionState] = useState(params.get("decision") ?? "");
  const [q, setQ] = useState(params.get("q") ?? "");
  const [submittedQ, setSubmittedQ] = useState(params.get("q") ?? "");

  const syncUrl = (nextDomain: string, nextDecision: string, nextQ: string) => {
    const query = new URLSearchParams();
    if (nextDomain) query.set("domain", nextDomain);
    if (nextDecision) query.set("decision", nextDecision);
    if (nextQ) query.set("q", nextQ);
    const suffix = query.toString();
    router.replace(`/dashboard/experiments/decisions${suffix ? `?${suffix}` : ""}`, {
      scroll: false,
    });
  };

  const list = useQuery({
    queryKey: ["experiment-decisions", domain, decision, submittedQ],
    queryFn: () => {
      const query = new URLSearchParams({ limit: "50" });
      if (domain) query.set("domain", domain);
      if (decision) query.set("decision", decision);
      if (submittedQ) query.set("q", submittedQ);
      return apiWithAuth<{ data: DecisionRecord[]; meta: { total: number } }>(
        `/experiments/decisions?${query.toString()}`,
      );
    },
  });
  const meta = useQuery({
    queryKey: ["experiment-decisions-meta", domain],
    queryFn: () =>
      apiWithAuth<{
        data: { total: number; by_decision: Record<string, number>; win_rate: number | null };
      }>(`/experiments/decisions/meta${domain ? `?domain=${domain}` : ""}`),
  });

  const records = list.data?.data ?? [];
  const corpus = meta.data?.data;

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <h1 className="text-xl font-semibold">Decision registry</h1>
      {corpus ? (
        <div className="flex flex-wrap gap-4 text-sm text-slate-600">
          <span>
            total: <strong>{corpus.total}</strong>
          </span>
          {Object.entries(corpus.by_decision).map(([k, v]) => (
            <span key={k}>
              {k}: <strong>{v}</strong>
            </span>
          ))}
          <span>
            randomized win-rate:{" "}
            <strong>
              {corpus.win_rate == null ? "—" : `${(corpus.win_rate * 100).toFixed(0)}%`}
            </strong>
          </span>
        </div>
      ) : null}
      <div className="flex flex-wrap items-end gap-3">
        <label className="text-xs text-slate-600">
          Domain
          <select
            aria-label="Domain filter"
            className="block rounded-md border px-2 py-1 text-sm"
            value={domain}
            onChange={(e) => {
              setDomainState(e.target.value);
              syncUrl(e.target.value, decision, submittedQ);
            }}
          >
            <option value="">all</option>
            {EXPERIMENT_DOMAINS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs text-slate-600">
          Decision
          <select
            aria-label="Decision filter"
            className="block rounded-md border px-2 py-1 text-sm"
            value={decision}
            onChange={(e) => {
              setDecisionState(e.target.value);
              syncUrl(domain, e.target.value, submittedQ);
            }}
          >
            <option value="">all</option>
            {DECISIONS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setSubmittedQ(q);
            syncUrl(domain, decision, q);
          }}
          className="flex items-end gap-2"
        >
          <label className="text-xs text-slate-600">
            Search summaries
            <input
              className="block w-64 rounded-md border px-2 py-1 text-sm"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </label>
          <button type="submit" className="rounded-md border px-3 py-1.5 text-sm">
            Search
          </button>
        </form>
      </div>
      <SectionCard title={`Records (${list.data?.meta.total ?? 0})`}>
        {records.length === 0 ? (
          <EmptyState message="No decisions recorded yet — organizational memory starts here." />
        ) : (
          <ul className="space-y-2">
            {records.map((r) => (
              <li key={r.id} className="rounded-md border p-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <Pill value={r.decision} styles={DECISION_STYLES} />
                  <span className="text-xs text-slate-500">{r.domain}</span>
                  <span className="text-xs text-slate-500">{r.analysis_type}</span>
                  {r.guardrail_outcome?.clean === false ? (
                    <span className="text-xs text-rose-600">guardrail events</span>
                  ) : null}
                  <span className="ml-auto text-xs text-slate-400">{fmtDate(r.created_at)}</span>
                </div>
                <Link
                  href={`/dashboard/experiments/decisions/${r.id}`}
                  className="mt-1 block hover:underline"
                >
                  {r.summary}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>
    </div>
  );
}
