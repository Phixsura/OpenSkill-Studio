"use client";
/** Experiment Console — list (ADR-017 Part L). Status/domain filters are
 * shareable URL state (R393 precedent); the list is keyset-paginated with
 * Load more and meta totals; Load-more failures surface in the error banner. */

import Link from "next/link";
import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { usePlatformAdmin } from "@/lib/use-me";
import { EmptyState, ErrorBanner, ExperimentsNav, Pill } from "./components";
import {
  EXPERIMENT_DOMAINS,
  EXPERIMENT_STATUSES,
  STATUS_STYLES,
  fmtDate,
  fmtPct,
  type Experiment,
} from "./lib";

export default function ExperimentsPage() {
  return (
    <Suspense>
      <ExperimentsInner />
    </Suspense>
  );
}

function ExperimentsInner() {
  const isPlatformAdmin = usePlatformAdmin();
  const router = useRouter();
  const params = useSearchParams();
  const [status, setStatusState] = useState(params.get("status") ?? "");
  const [domain, setDomainState] = useState(params.get("domain") ?? "");
  const [pages, setPages] = useState<Experiment[][]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const syncUrl = (nextStatus: string, nextDomain: string) => {
    const query = new URLSearchParams();
    if (nextStatus) query.set("status", nextStatus);
    if (nextDomain) query.set("domain", nextDomain);
    const suffix = query.toString();
    router.replace(`/dashboard/experiments${suffix ? `?${suffix}` : ""}`, { scroll: false });
  };
  const setStatus = (v: string) => {
    setStatusState(v);
    setPages([]);
    setCursor(null);
    syncUrl(v, domain);
  };
  const setDomain = (v: string) => {
    setDomainState(v);
    setPages([]);
    setCursor(null);
    syncUrl(status, v);
  };

  const { data, isLoading } = useQuery({
    queryKey: ["experiments", status, domain, cursor],
    queryFn: async () => {
      try {
        const query = new URLSearchParams({ limit: "50" });
        if (status) query.set("status", status);
        if (domain) query.set("domain", domain);
        if (cursor) query.set("cursor", cursor);
        const res = await apiWithAuth<{
          data: Experiment[];
          meta: { total: number; next_cursor: string | null };
        }>(`/experiments?${query.toString()}`);
        setPages((prev) => (cursor ? [...prev, res.data] : [res.data]));
        setError(null);
        return res;
      } catch (e) {
        setError(e instanceof ApiError ? e.message : "Failed to load experiments");
        throw e;
      }
    },
  });

  const experiments = pages.flat();
  const total = data?.meta?.total ?? 0;
  const nextCursor = data?.meta?.next_cursor ?? null;

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Experiments</h1>
        {isPlatformAdmin ? (
          <Link
            href="/dashboard/experiments/new"
            className="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white"
          >
            New experiment
          </Link>
        ) : null}
      </div>
      <ErrorBanner message={error} />
      <div className="flex flex-wrap gap-3">
        <label className="text-sm text-slate-600">
          Status{" "}
          <select
            aria-label="Status filter"
            className="rounded-md border px-2 py-1 text-sm"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">all</option>
            {EXPERIMENT_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm text-slate-600">
          Domain{" "}
          <select
            aria-label="Domain filter"
            className="rounded-md border px-2 py-1 text-sm"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
          >
            <option value="">all</option>
            {EXPERIMENT_DOMAINS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
      </div>
      {isLoading && experiments.length === 0 ? (
        <div className="text-sm text-slate-500">Loading…</div>
      ) : experiments.length === 0 ? (
        <EmptyState message="No experiments match the current filters." />
      ) : (
        <div className="overflow-x-auto rounded-lg border bg-white">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-3 py-2">Experiment</th>
                <th className="px-3 py-2">Domain</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Ramp</th>
                <th className="px-3 py-2">Risk</th>
                <th className="px-3 py-2">Started</th>
              </tr>
            </thead>
            <tbody>
              {experiments.map((experiment) => (
                <tr key={experiment.id} className="border-t hover:bg-slate-50">
                  <td className="px-3 py-2">
                    <Link
                      href={`/dashboard/experiments/${experiment.id}`}
                      className="font-medium text-slate-900 hover:underline"
                    >
                      {experiment.title}
                    </Link>
                    <div className="text-xs text-slate-500">{experiment.key}</div>
                  </td>
                  <td className="px-3 py-2">{experiment.domain}</td>
                  <td className="px-3 py-2">
                    <Pill value={experiment.status} styles={STATUS_STYLES} />
                  </td>
                  <td className="px-3 py-2">{fmtPct(experiment.ramp_bp)}</td>
                  <td className="px-3 py-2">{experiment.risk_class}</td>
                  <td className="px-3 py-2">{fmtDate(experiment.started_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="flex items-center gap-3 text-sm text-slate-600">
        <span>
          {experiments.length} of {total}
        </span>
        {nextCursor ? (
          <button
            type="button"
            className="rounded-md border px-3 py-1.5"
            onClick={() => setCursor(nextCursor)}
          >
            Load more
          </button>
        ) : null}
      </div>
    </div>
  );
}
