"use client";
/** External source registry (ADR-016 Part A). */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill } from "../components";
import { STATUS_STYLES, fmtDate } from "../lib";

interface Source {
  id: string;
  name: string;
  source_type: string;
  trust_level: string;
  base_url: string | null;
  adapter_key: string;
  status: string;
  last_success_at: string | null;
  consecutive_failures: number;
  robots_compliant: boolean;
}

const SOURCE_TYPES = [
  "provider_api",
  "model_docs_feed",
  "github_repo",
  "huggingface",
  "comfyui_repo",
  "pricing_feed",
  "internal_research",
  "manual_analyst",
];
const TRUST_LEVELS = ["official", "verified_partner", "community", "unverified", "internal"];
const ADAPTERS = [
  "json_catalog",
  "pricing_json",
  "github_releases",
  "huggingface",
  "comfyui_repo",
  "manual",
];

interface SourceHealth {
  runs: number;
  success_rate: number | null;
  by_status: Record<string, number>;
  observations_created: number;
  bytes_fetched: number;
  last_error: string | null;
}

export default function SourcesPage() {
  const queryClient = useQueryClient();
  const [healthFor, setHealthFor] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "",
    source_type: "provider_api",
    trust_level: "official",
    adapter_key: "json_catalog",
    base_url: "",
    robots_compliant: true,
  });

  const { data, isLoading } = useQuery({
    queryKey: ["eco-sources"],
    queryFn: () => apiWithAuth<{ data: Source[] }>("/ecosystem/sources"),
  });
  const health = useQuery({
    queryKey: ["eco-source-health", healthFor],
    enabled: Boolean(healthFor),
    queryFn: () => apiWithAuth<{ data: SourceHealth }>(`/ecosystem/sources/${healthFor}/health`),
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["eco-sources"] });

  const createSource = useMutation({
    mutationFn: () =>
      apiWithAuth("/ecosystem/sources", {
        method: "POST",
        body: JSON.stringify({ ...form, base_url: form.base_url || null }),
      }),
    onSuccess: () => {
      setShowForm(false);
      setError(null);
      invalidate();
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Failed to create source"),
  });

  const syncSource = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`/ecosystem/sources/${id}/sync`, { method: "POST", body: "{}" }),
    onSuccess: () => {
      setError(null);
      invalidate();
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Sync failed"),
  });

  const toggleStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      apiWithAuth(`/ecosystem/sources/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
    onSuccess: invalidate,
  });

  const sources = data?.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">External Sources</h1>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm text-[hsl(var(--primary-foreground))]"
        >
          {showForm ? "Cancel" : "Register source"}
        </button>
      </div>
      <EcosystemNav />
      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}
      {showForm && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            createSource.mutate();
          }}
          className="grid gap-3 rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm md:grid-cols-2"
        >
          <input
            required
            placeholder="Source name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
          />
          <input
            placeholder="Base URL (https://…)"
            value={form.base_url}
            onChange={(e) => setForm({ ...form, base_url: e.target.value })}
            className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
          />
          <select
            value={form.source_type}
            onChange={(e) => setForm({ ...form, source_type: e.target.value })}
            className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
          >
            {SOURCE_TYPES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <select
            value={form.trust_level}
            onChange={(e) => setForm({ ...form, trust_level: e.target.value })}
            className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
          >
            {TRUST_LEVELS.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <select
            value={form.adapter_key}
            onChange={(e) => setForm({ ...form, adapter_key: e.target.value })}
            className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
          >
            {ADAPTERS.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.robots_compliant}
              onChange={(e) => setForm({ ...form, robots_compliant: e.target.checked })}
            />
            I attest syncing this source respects its robots/ToS
          </label>
          <button
            type="submit"
            disabled={createSource.isPending}
            className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm text-[hsl(var(--primary-foreground))] md:col-span-2"
          >
            Create
          </button>
        </form>
      )}
      {isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading sources…</div>
      ) : sources.length === 0 ? (
        <EmptyState icon="🛰️" text="No sources registered yet." />
      ) : (
        <div className="overflow-x-auto rounded-lg border shadow-sm">
          <table className="w-full">
            <thead className="bg-[hsl(var(--secondary))]">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Trust</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Last success</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {sources.map((s) => (
                <tr key={s.id} className="bg-[hsl(var(--card))]">
                  <td className="px-4 py-3 text-sm font-medium">
                    {s.name}
                    <div className="text-xs text-[hsl(var(--muted-foreground))]">{s.base_url}</div>
                  </td>
                  <td className="px-4 py-3 text-sm">{s.source_type}</td>
                  <td className="px-4 py-3 text-sm">{s.trust_level}</td>
                  <td className="px-4 py-3">
                    <Pill value={s.status} styles={STATUS_STYLES} />
                    {s.consecutive_failures > 0 && (
                      <span className="ml-2 text-xs text-red-600">
                        {s.consecutive_failures} failures
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-[hsl(var(--muted-foreground))]">
                    {fmtDate(s.last_success_at)}
                  </td>
                  <td className="space-x-2 px-4 py-3 text-sm">
                    <button
                      onClick={() => syncSource.mutate(s.id)}
                      disabled={syncSource.isPending || s.status !== "active"}
                      className="rounded-md border px-2 py-1 text-xs hover:bg-[hsl(var(--secondary))]"
                    >
                      Sync now
                    </button>
                    <button
                      onClick={() => setHealthFor(healthFor === s.id ? null : s.id)}
                      className="rounded-md border px-2 py-1 text-xs hover:bg-[hsl(var(--secondary))]"
                    >
                      Health
                    </button>
                    <button
                      onClick={() =>
                        toggleStatus.mutate({
                          id: s.id,
                          status: s.status === "paused" ? "active" : "paused",
                        })
                      }
                      className="rounded-md border px-2 py-1 text-xs hover:bg-[hsl(var(--secondary))]"
                    >
                      {s.status === "paused" ? "Resume" : "Pause"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {healthFor && health.data?.data && (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-4 text-sm shadow-sm">
          <h3 className="mb-2 font-semibold">Source health (7d)</h3>
          <div className="grid gap-2 md:grid-cols-4">
            <div>runs: {health.data.data.runs}</div>
            <div>
              success rate:{" "}
              {health.data.data.success_rate != null
                ? `${(health.data.data.success_rate * 100).toFixed(0)}%`
                : "—"}
            </div>
            <div>observations: {health.data.data.observations_created}</div>
            <div>bytes: {health.data.data.bytes_fetched}</div>
          </div>
          {health.data.data.last_error && (
            <div className="mt-2 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs text-red-700">
              last error: {health.data.data.last_error}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
