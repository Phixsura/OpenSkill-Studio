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

export default function HoldoutGroupsPage() {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ key: "", title: "", domain: "learning", holdout_bp: "500" });

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
        }),
      }),
    onSuccess: () => {
      setError(null);
      setForm({ key: "", title: "", domain: form.domain, holdout_bp: "500" });
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
                    {g.status === "active" ? (
                      <button
                        type="button"
                        onClick={() => release.mutate(g.id)}
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
      </SectionCard>
    </div>
  );
}
