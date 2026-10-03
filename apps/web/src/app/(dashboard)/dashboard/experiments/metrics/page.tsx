"use client";
/** Metric explorer — the semantic layer over product data (ADR-017 Part C).
 * Definitions carry provenance (query_version) and robustness knobs. */

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EmptyState, ErrorBanner, ExperimentsNav, SectionCard } from "../components";
import { EXPERIMENT_DOMAINS, METRIC_DIRECTIONS } from "../lib";

interface MetricDefinition {
  id: string;
  key: string;
  title: string;
  kind: string;
  domain: string;
  source_kind: string;
  query_version: number;
  spec: { source?: string; measure?: string };
  direction: string;
  winsorize_pct: number | null;
}

export default function MetricExplorerPage() {
  return (
    <Suspense>
      <MetricExplorerInner />
    </Suspense>
  );
}

function MetricExplorerInner() {
  const router = useRouter();
  const params = useSearchParams();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [domain, setDomainState] = useState(params.get("domain") ?? "");
  const setDomain = (v: string) => {
    setDomainState(v);
    router.replace(`/dashboard/experiments/metrics${v ? `?domain=${v}` : ""}`, { scroll: false });
  };

  const { data, isLoading } = useQuery({
    queryKey: ["experiment-metric-definitions", domain],
    queryFn: () =>
      apiWithAuth<{ data: MetricDefinition[] }>(
        `/experiments/metric-definitions${domain ? `?domain=${domain}` : ""}`,
      ),
  });

  const seed = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: { created: number } }>("/experiments/metric-definitions/seed", {
        method: "POST",
        body: "{}",
      }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["experiment-metric-definitions"] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Seed failed"),
  });

  const definitions = data?.data ?? [];
  const [editing, setEditing] = useState<string | null>(null);
  const [edit, setEdit] = useState({ winsorize_pct: "", cap_value: "", direction: "" });
  const save = useMutation({
    mutationFn: (key: string) =>
      apiWithAuth(`/experiments/metric-definitions/${key}`, {
        method: "PATCH",
        body: JSON.stringify({
          ...(edit.direction ? { direction: edit.direction } : {}),
          ...(edit.winsorize_pct
            ? { winsorize_pct: Number(edit.winsorize_pct) }
            : { clear_winsorize: true }),
          ...(edit.cap_value ? { cap_value: Number(edit.cap_value) } : { clear_cap: true }),
        }),
      }),
    onSuccess: () => {
      setEditing(null);
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["experiment-metric-definitions"] });
    },
    onError: (e: Error) => setError(e.message),
  });

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Metric explorer</h1>
        <button
          type="button"
          onClick={() => seed.mutate()}
          className="rounded-md border px-3 py-1.5 text-sm"
        >
          Seed built-in definitions
        </button>
      </div>
      <ErrorBanner message={error} />
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
      <SectionCard title={`Definitions (${definitions.length})`}>
        {isLoading ? (
          <div className="text-sm text-slate-500">Loading…</div>
        ) : definitions.length === 0 ? (
          <EmptyState message="No metric definitions — seed the built-ins to start." />
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="py-1 pr-3">Key</th>
                <th className="py-1 pr-3">Kind</th>
                <th className="py-1 pr-3">Domain</th>
                <th className="py-1 pr-3">Source</th>
                <th className="py-1 pr-3">qv</th>
                <th className="py-1 pr-3">Direction</th>
                <th className="py-1 pr-3">Winsorize</th>
                <th className="py-1 pr-3" />
              </tr>
            </thead>
            <tbody>
              {definitions.map((d) => (
                <tr key={d.id} className="border-t">
                  <td className="py-1 pr-3">
                    <span className="font-medium">{d.key}</span>
                    <div className="text-xs text-slate-500">{d.title}</div>
                  </td>
                  <td className="py-1 pr-3">{d.kind}</td>
                  <td className="py-1 pr-3">{d.domain}</td>
                  <td className="py-1 pr-3 text-xs">
                    {d.spec?.source ?? "—"}
                    {d.spec?.measure ? ` · ${d.spec.measure}` : ""}
                  </td>
                  <td className="py-1 pr-3">{d.query_version}</td>
                  <td className="py-1 pr-3 text-xs">{d.direction}</td>
                  <td className="py-1 pr-3 text-xs">{d.winsorize_pct ?? "—"}</td>
                  <td className="py-1 pr-3 text-xs">
                    {editing === d.key ? (
                      <span className="flex items-center gap-1">
                        <input
                          aria-label={`winsorize ${d.key}`}
                          className="w-16 rounded border px-1 py-0.5"
                          placeholder="wins%"
                          value={edit.winsorize_pct}
                          onChange={(e) => setEdit({ ...edit, winsorize_pct: e.target.value })}
                        />
                        <input
                          aria-label={`cap ${d.key}`}
                          className="w-20 rounded border px-1 py-0.5"
                          placeholder="cap"
                          value={edit.cap_value}
                          onChange={(e) => setEdit({ ...edit, cap_value: e.target.value })}
                        />
                        <select
                          aria-label={`direction ${d.key}`}
                          className="rounded border px-1 py-0.5"
                          value={edit.direction}
                          onChange={(e) => setEdit({ ...edit, direction: e.target.value })}
                        >
                          <option value="">dir…</option>
                          {METRIC_DIRECTIONS.map((dir) => (
                            <option key={dir} value={dir}>
                              {dir}
                            </option>
                          ))}
                        </select>
                        <button
                          type="button"
                          className="rounded border px-2 py-0.5"
                          onClick={() => save.mutate(d.key)}
                        >
                          Save
                        </button>
                        <button type="button" className="px-1" onClick={() => setEditing(null)}>
                          ✕
                        </button>
                      </span>
                    ) : (
                      <button
                        type="button"
                        className="rounded border px-2 py-0.5"
                        onClick={() => {
                          setEditing(d.key);
                          setEdit({
                            winsorize_pct: d.winsorize_pct?.toString() ?? "",
                            cap_value: "",
                            direction: "",
                          });
                        }}
                      >
                        Edit
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </SectionCard>
    </div>
  );
}
