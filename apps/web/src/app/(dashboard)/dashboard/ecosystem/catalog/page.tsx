"use client";
/** Canonical AI ecosystem catalog + lifecycle + conflicts (Parts C/L/Q). */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill } from "../components";
import { LIFECYCLE_STYLES, fmtDate } from "../lib";

const KINDS = [
  { segment: "models", label: "Models" },
  { segment: "model-versions", label: "Model Versions" },
  { segment: "providers", label: "Providers" },
  { segment: "tools", label: "Tools" },
  { segment: "workflows", label: "Workflows" },
  { segment: "agents", label: "Agents" },
  { segment: "node-packages", label: "Node Packages" },
];

const TRANSITIONS: Record<string, string[]> = {
  discovered: ["under_review", "blocked"],
  under_review: ["verified", "blocked", "discovered"],
  verified: ["recommended", "watch", "deprecated", "blocked"],
  recommended: ["watch", "deprecated", "blocked"],
  watch: ["recommended", "deprecated", "blocked"],
  deprecated: ["retired", "watch"],
  blocked: ["under_review", "retired"],
  retired: [],
};

interface Entity {
  id: string;
  canonical_name: string;
  lifecycle_status: string;
  created_at: string;
  version?: string;
  sunset_at?: string | null;
  license?: string | null;
}

interface Conflict {
  field: string;
  values: Record<string, string[]>;
}

export default function CatalogPage() {
  const queryClient = useQueryClient();
  const [segment, setSegment] = useState("models");
  const [selected, setSelected] = useState<Entity | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["eco-catalog", segment],
    queryFn: () =>
      apiWithAuth<{ data: Entity[]; meta: { total: number } }>(
        `/ecosystem/catalog/${segment}?limit=100`,
      ),
  });
  const conflicts = useQuery({
    queryKey: ["eco-conflicts", segment, selected?.id],
    enabled: Boolean(selected),
    queryFn: () =>
      apiWithAuth<{ data: Conflict[] }>(`/ecosystem/catalog/${segment}/${selected!.id}/conflicts`),
  });

  const transition = useMutation({
    mutationFn: ({ id, to }: { id: string; to: string }) =>
      apiWithAuth(`/ecosystem/catalog/${segment}/${id}/lifecycle`, {
        method: "POST",
        body: JSON.stringify({
          to_status: to,
          reason: to === "deprecated" ? "manual_decision" : undefined,
        }),
      }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["eco-catalog", segment] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Transition failed"),
  });

  const rows = data?.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Model / Tool Catalog</h1>
      <EcosystemNav />
      <div className="flex flex-wrap gap-2">
        {KINDS.map((k) => (
          <button
            key={k.segment}
            onClick={() => {
              setSegment(k.segment);
              setSelected(null);
            }}
            className={`rounded-md px-3 py-1.5 text-sm ${
              segment === k.segment
                ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                : "bg-[hsl(var(--secondary))]"
            }`}
          >
            {k.label}
          </button>
        ))}
      </div>
      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}
      {isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading catalog…</div>
      ) : rows.length === 0 ? (
        <EmptyState
          icon="📚"
          text="Nothing in this catalog yet. Confirm discoveries to populate it."
        />
      ) : (
        <div className="overflow-x-auto rounded-lg border shadow-sm">
          <table className="w-full">
            <thead className="bg-[hsl(var(--secondary))]">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Lifecycle</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Sunset</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Transition</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Conflicts</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {rows.map((entity) => (
                <tr key={entity.id} className="bg-[hsl(var(--card))]">
                  <td className="px-4 py-3 text-sm font-medium">{entity.canonical_name}</td>
                  <td className="px-4 py-3">
                    <Pill value={entity.lifecycle_status} styles={LIFECYCLE_STYLES} />
                  </td>
                  <td className="px-4 py-3 text-sm text-[hsl(var(--muted-foreground))]">
                    {entity.sunset_at ? fmtDate(entity.sunset_at) : "—"}
                  </td>
                  <td className="px-4 py-3">
                    <select
                      defaultValue=""
                      onChange={(e) => {
                        if (e.target.value) {
                          transition.mutate({ id: entity.id, to: e.target.value });
                          e.target.value = "";
                        }
                      }}
                      className="rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
                    >
                      <option value="">Move to…</option>
                      {(TRANSITIONS[entity.lifecycle_status] ?? []).map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => setSelected(entity)}
                      className="rounded-md border px-2 py-1 text-xs hover:bg-[hsl(var(--secondary))]"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {selected && (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
          <h3 className="text-sm font-semibold">Source conflicts for {selected.canonical_name}</h3>
          {(conflicts.data?.data ?? []).length === 0 ? (
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              No disagreeing sources — all observations align.
            </p>
          ) : (
            <ul className="mt-2 space-y-2 text-sm">
              {(conflicts.data?.data ?? []).map((c) => (
                <li key={c.field} className="rounded-md border border-amber-300 bg-amber-50 p-3">
                  <span className="font-medium">{c.field}</span>: sources disagree —{" "}
                  {Object.entries(c.values)
                    .map(([value, sources]) => `"${value}" (${sources.length} source(s))`)
                    .join(" vs ")}
                  <div className="mt-1 text-xs text-amber-700">
                    Both observations are retained; no merged truth is invented.
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
