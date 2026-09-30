"use client";
/** Mutual-exclusion layers & slice allocations (ADR-017 Part B). */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EmptyState, ErrorBanner, ExperimentsNav, SectionCard } from "../components";
import { EXPERIMENT_DOMAINS } from "../lib";

interface Layer {
  id: string;
  key: string;
  domain: string;
  total_slices: number;
}

interface Allocation {
  id: string;
  experiment_id: string;
  slice_start: number;
  slice_end: number;
}

export default function LayersPage() {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [form, setForm] = useState({ key: "", domain: "learning" });
  const [alloc, setAlloc] = useState({ experiment_id: "", slice_start: "0", slice_end: "9999" });

  const layers = useQuery({
    queryKey: ["experiment-layers"],
    queryFn: () => apiWithAuth<{ data: Layer[] }>("/experiments/layers"),
  });
  const allocations = useQuery({
    queryKey: ["experiment-layer-allocations", selected],
    enabled: Boolean(selected),
    queryFn: () =>
      apiWithAuth<{ data: Allocation[] }>(`/experiments/layers/${selected}/allocations`),
  });

  const createLayer = useMutation({
    mutationFn: () =>
      apiWithAuth("/experiments/layers", { method: "POST", body: JSON.stringify(form) }),
    onSuccess: () => {
      setError(null);
      setForm({ key: "", domain: form.domain });
      queryClient.invalidateQueries({ queryKey: ["experiment-layers"] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Failed to create layer"),
  });

  const allocate = useMutation({
    mutationFn: () =>
      apiWithAuth(`/experiments/layers/${selected}/allocations`, {
        method: "POST",
        body: JSON.stringify({
          experiment_id: alloc.experiment_id,
          slice_start: Number(alloc.slice_start),
          slice_end: Number(alloc.slice_end),
        }),
      }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["experiment-layer-allocations", selected] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Allocation failed"),
  });

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <h1 className="text-xl font-semibold">Layers (mutual exclusion)</h1>
      <p className="text-sm text-slate-600">
        Same-layer experiments own disjoint slice ranges of the [0, 10000) hash space — one unit can
        never enter two incompatible experiments.
      </p>
      <ErrorBanner message={error} />
      <SectionCard title="Create layer">
        <div className="flex flex-wrap items-end gap-2">
          <label className="text-xs text-slate-600">
            Key
            <input
              className="block rounded-md border px-2 py-1 text-sm"
              value={form.key}
              onChange={(e) => setForm({ ...form, key: e.target.value })}
              placeholder="learning-core"
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
          <button
            type="button"
            onClick={() => createLayer.mutate()}
            className="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white"
          >
            Create
          </button>
        </div>
      </SectionCard>
      <SectionCard title="Layers">
        {(layers.data?.data ?? []).length === 0 ? (
          <EmptyState message="No layers yet — create one per domain to start allocating slices." />
        ) : (
          <ul className="space-y-1 text-sm">
            {(layers.data?.data ?? []).map((layer) => (
              <li key={layer.id}>
                <button
                  type="button"
                  className={`rounded px-2 py-1 hover:bg-slate-50 ${selected === layer.key ? "bg-slate-100 font-medium" : ""}`}
                  onClick={() => setSelected(layer.key)}
                >
                  {layer.key} <span className="text-xs text-slate-500">({layer.domain})</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>
      {selected ? (
        <SectionCard title={`Allocations in ${selected}`}>
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="py-1 pr-3">Experiment</th>
                <th className="py-1 pr-3">Slice range</th>
              </tr>
            </thead>
            <tbody>
              {(allocations.data?.data ?? []).map((a) => (
                <tr key={a.id} className="border-t">
                  <td className="py-1 pr-3 text-xs">{a.experiment_id}</td>
                  <td className="py-1 pr-3">
                    [{a.slice_start}, {a.slice_end}]
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-3 flex flex-wrap items-end gap-2">
            <label className="text-xs text-slate-600">
              Experiment id
              <input
                className="block w-64 rounded-md border px-2 py-1 text-sm"
                value={alloc.experiment_id}
                onChange={(e) => setAlloc({ ...alloc, experiment_id: e.target.value })}
              />
            </label>
            <label className="text-xs text-slate-600">
              Start
              <input
                className="block w-20 rounded-md border px-2 py-1 text-sm"
                value={alloc.slice_start}
                onChange={(e) => setAlloc({ ...alloc, slice_start: e.target.value })}
              />
            </label>
            <label className="text-xs text-slate-600">
              End
              <input
                className="block w-20 rounded-md border px-2 py-1 text-sm"
                value={alloc.slice_end}
                onChange={(e) => setAlloc({ ...alloc, slice_end: e.target.value })}
              />
            </label>
            <button
              type="button"
              onClick={() => allocate.mutate()}
              className="rounded-md border px-3 py-1.5 text-sm"
            >
              Allocate
            </button>
          </div>
        </SectionCard>
      ) : null}
    </div>
  );
}
