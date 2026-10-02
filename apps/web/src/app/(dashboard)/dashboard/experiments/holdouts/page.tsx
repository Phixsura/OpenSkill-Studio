"use client";
/** Global holdout groups (ADR-017 §4.12 v2) — domain-wide long-term control. */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EmptyState, ErrorBanner, ExperimentsNav, SectionCard } from "../components";
import { EXPERIMENT_DOMAINS } from "../lib";

interface HoldoutGroup {
  id: string;
  key: string;
  title: string;
  domain: string;
  scope_org_id: string | null;
  holdout_bp: number;
  status: string;
  starts_at: string;
  ends_at: string | null;
}

interface HoldoutReport {
  group_key: string;
  metric_key: string;
  window_days: number;
  sampled_units: number;
  holdout_units: number;
  general_units: number;
  arms: Record<string, { n?: number; numerator?: number; denominator?: number }>;
  comparison: { effect?: number; p?: number } | null;
  caveat: string;
}

export default function HoldoutGroupsPage() {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [reportMetric, setReportMetric] = useState("project_approval_rate");
  const [report, setReport] = useState<HoldoutReport | null>(null);
  const runReport = useMutation({
    mutationFn: (groupId: string) =>
      apiWithAuth<{ data: HoldoutReport }>(
        `/experiments/holdout-groups/${groupId}/report?metric_key=${encodeURIComponent(
          reportMetric,
        )}`,
      ),
    onSuccess: (r) => {
      setReport(r.data);
      setError(null);
    },
    onError: (e: Error) => setError(e.message),
  });
  const [form, setForm] = useState({
    key: "",
    title: "",
    domain: "learning",
    holdout_bp: "500",
    scope_org_id: "",
    ends_at: "",
  });

  const definitions = useQuery({
    queryKey: ["experiment-metric-definitions"],
    queryFn: () =>
      apiWithAuth<{ data: { key: string; spec?: { source?: string } }[] }>(
        "/experiments/metric-definitions",
      ),
  });
  const reportableSources = new Set([
    "projects",
    "cost_ledger",
    "evaluations",
    "learning_paths",
    "client_briefs",
    "registry",
  ]);
  const reportableKeys = (definitions.data?.data ?? [])
    .filter((d) => reportableSources.has(d.spec?.source ?? ""))
    .map((d) => d.key);

  const groups = useQuery({
    queryKey: ["experiment-holdout-groups"],
    queryFn: () => apiWithAuth<{ data: HoldoutGroup[] }>("/experiments/holdout-groups"),
  });

  const createGroup = useMutation({
    mutationFn: () =>
      apiWithAuth("/experiments/holdout-groups", {
        method: "POST",
        body: JSON.stringify({
          key: form.key,
          title: form.title,
          domain: form.domain,
          holdout_bp: Number(form.holdout_bp),
          scope_org_id: form.scope_org_id || null,
          ends_at: form.ends_at ? new Date(form.ends_at).toISOString() : null,
        }),
      }),
    onSuccess: () => {
      setError(null);
      setForm({
        key: "",
        title: "",
        domain: form.domain,
        holdout_bp: "500",
        scope_org_id: "",
        ends_at: "",
      });
      queryClient.invalidateQueries({ queryKey: ["experiment-holdout-groups"] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Failed to create holdout group"),
  });

  const release = useMutation({
    mutationFn: (groupId: string) =>
      apiWithAuth(`/experiments/holdout-groups/${groupId}/release`, { method: "POST" }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["experiment-holdout-groups"] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Release failed"),
  });

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <h1 className="text-xl font-semibold">Global holdout groups</h1>
      <p className="text-sm text-slate-600">
        A holdout group withholds a hash band of units from NEW enrollment into every experiment of
        its domain — the long-term counterfactual for everything shipped. Existing assignments keep
        serving; releasing the group frees its units instantly.
      </p>
      <ErrorBanner message={error} />
      <SectionCard title="Create holdout group">
        <div className="flex flex-wrap items-end gap-2">
          <label className="text-xs text-slate-600">
            Key
            <input
              className="block rounded-md border px-2 py-1 text-sm"
              value={form.key}
              onChange={(e) => setForm({ ...form, key: e.target.value })}
              placeholder="q4-learning-holdout"
            />
          </label>
          <label className="text-xs text-slate-600">
            Title
            <input
              className="block w-56 rounded-md border px-2 py-1 text-sm"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Q4 learning holdout"
            />
          </label>
          <label className="text-xs text-slate-600">
            Domain
            <select
              className="block rounded-md border px-2 py-1 text-sm"
              value={form.domain}
              onChange={(e) => setForm({ ...form, domain: e.target.value })}
            >
              {EXPERIMENT_DOMAINS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </label>
          <label className="text-xs text-slate-600">
            Holdout (bp, max 2000)
            <input
              className="block w-24 rounded-md border px-2 py-1 text-sm"
              value={form.holdout_bp}
              onChange={(e) => setForm({ ...form, holdout_bp: e.target.value })}
            />
          </label>
          <label className="text-xs text-slate-600">
            Scope org id (optional)
            <input
              className="block w-56 rounded-md border px-2 py-1 text-sm"
              value={form.scope_org_id}
              onChange={(e) => setForm({ ...form, scope_org_id: e.target.value })}
              placeholder="platform-wide when empty"
            />
          </label>
          <label className="text-xs text-slate-600">
            Ends (optional)
            <input
              type="date"
              className="block rounded-md border px-2 py-1 text-sm"
              value={form.ends_at}
              onChange={(e) => setForm({ ...form, ends_at: e.target.value })}
            />
          </label>
          <button
            type="button"
            onClick={() => createGroup.mutate()}
            className="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white"
          >
            Create
          </button>
        </div>
      </SectionCard>
      <SectionCard title="Groups">
        {(groups.data?.data ?? []).length === 0 ? (
          <EmptyState message="No holdout groups — create one to reserve a domain-wide control band." />
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="py-1 pr-3">Key</th>
                <th className="py-1 pr-3">Domain</th>
                <th className="py-1 pr-3">Band</th>
                <th className="py-1 pr-3">Status</th>
                <th className="py-1 pr-3">Ends</th>
                <th className="py-1 pr-3" />
              </tr>
            </thead>
            <tbody>
              {(groups.data?.data ?? []).map((g) => (
                <tr key={g.id} className="border-t">
                  <td className="py-1 pr-3 font-medium">{g.key}</td>
                  <td className="py-1 pr-3">{g.domain}</td>
                  <td className="py-1 pr-3">{(g.holdout_bp / 100).toFixed(1)}%</td>
                  <td className="py-1 pr-3">{g.status}</td>
                  <td className="py-1 pr-3 text-xs">
                    {g.ends_at ? new Date(g.ends_at).toLocaleDateString() : "—"}
                  </td>
                  <td className="py-1 pr-3">
                    <button
                      type="button"
                      onClick={() => runReport.mutate(g.id)}
                      className="mr-2 rounded-md border px-2 py-1 text-xs"
                    >
                      Report
                    </button>
                    {g.status === "active" ? (
                      <button
                        type="button"
                        onClick={() => {
                          if (
                            window.confirm(
                              `Release ${g.key}? Its units re-enter every ` +
                                "experiment in the domain immediately.",
                            )
                          ) {
                            release.mutate(g.id);
                          }
                        }}
                        className="rounded-md border px-2 py-1 text-xs"
                      >
                        Release
                      </button>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <div className="mt-3 flex items-center gap-2 text-xs text-slate-600">
          <label htmlFor="hg-report-metric">Report metric</label>
          <input
            id="hg-report-metric"
            className="rounded-md border px-2 py-1"
            list="hg-reportable-metrics"
            value={reportMetric}
            onChange={(e) => setReportMetric(e.target.value)}
          />
          <datalist id="hg-reportable-metrics">
            {reportableKeys.map((k) => (
              <option key={k} value={k} />
            ))}
          </datalist>
        </div>
        {report ? (
          <div className="mt-3 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm">
            <div className="font-medium">
              {report.group_key} · {report.metric_key} · last {report.window_days}d
            </div>
            <div className="mt-1 text-xs text-slate-600">
              {report.holdout_units.toLocaleString()} held out /{" "}
              {report.general_units.toLocaleString()} general (of{" "}
              {report.sampled_units.toLocaleString()} sampled)
            </div>
            <div className="mt-1">
              {Object.entries(report.arms).map(([arm, v]) => (
                <span key={arm} className="mr-4">
                  {arm}:{" "}
                  {v.denominator
                    ? `${(((v.numerator ?? 0) / v.denominator) * 100).toFixed(1)}%`
                    : `n=${v.n ?? 0}`}
                </span>
              ))}
              {report.comparison?.p !== undefined ? (
                <span className="text-xs text-slate-500">
                  p = {report.comparison.p?.toFixed(4)}
                </span>
              ) : null}
            </div>
            <p className="mt-2 text-xs text-amber-700">{report.caveat}</p>
          </div>
        ) : null}
      </SectionCard>
    </div>
  );
}
