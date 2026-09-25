"use client";

import Link from "next/link";
/** Canonical AI ecosystem catalog + lifecycle + conflicts (Parts C/L/Q). */

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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

const SEGMENT_TO_KIND: Record<string, string> = {
  providers: "provider",
  tools: "tool",
  models: "model",
  "model-versions": "model_version",
  workflows: "workflow",
  agents: "agent",
  "node-packages": "node_package",
};

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
  curated?: { value: string; source_id: string | null; decided_at: string } | null;
}

interface DuplicatePair {
  a: { id: string; canonical_name: string; lifecycle_status: string };
  b: { id: string; canonical_name: string; lifecycle_status: string };
  similarity: number;
}

interface Corroboration {
  distinct_sources: number;
  trust_weighted_score: number;
  human_verified_any: boolean;
}

interface ScoreHistory {
  points: { value: number; finished_at: string | null }[];
  trend: { slope: number; projected_next: number } | null;
}

interface PriceHistory {
  series: Record<string, { price: number; currency: string; observed_at: string | null }[]>;
  trends: Record<string, { slope: number; projected_next: number } | null>;
}

interface Scorecard {
  grade: string;
  passing: number;
  applicable: number;
  checks: { check: string; status: string; evidence: Record<string, unknown> }[];
}

const CHECK_STYLES: Record<string, string> = {
  pass: "bg-emerald-100 text-emerald-800",
  warn: "bg-amber-100 text-amber-800",
  fail: "bg-red-100 text-red-800",
  "n/a": "bg-gray-100 text-gray-500",
};

export default function CatalogPage() {
  return (
    <Suspense>
      <CatalogInner />
    </Suspense>
  );
}

function CatalogInner() {
  const queryClient = useQueryClient();
  const router = useRouter();
  const params = useSearchParams();
  const [segment, setSegment] = useState(params.get("kind") ?? "models");
  const [selected, setSelected] = useState<Entity | null>(null);
  const [offset, setOffset] = useState(0);
  const [pages, setPages] = useState<Entity[][]>([]);
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["eco-catalog", segment, offset],
    queryFn: async () => {
      const res = await apiWithAuth<{ data: Entity[]; meta: { total: number } }>(
        `/ecosystem/catalog/${segment}?limit=100&offset=${offset}`,
      );
      setPages((prev) => (offset === 0 ? [res.data] : [...prev, res.data]));
      return res;
    },
  });
  const total = data?.meta?.total ?? 0;

  // Shareable deep link: /catalog?kind=models&entity=<id> restores Inspect
  useEffect(() => {
    const entityId = params.get("entity");
    if (entityId && entityId !== selected?.id) {
      const hit = pages.flat().find((e) => e.id === entityId);
      if (hit) {
        setSelected(hit);
      } else if (pages.length > 0) {
        // R165: the deep-linked entity may live beyond the loaded pages —
        // fetch it directly instead of silently dropping the link
        apiWithAuth<{ data: Entity }>(`/ecosystem/catalog/${segment}/${entityId}`)
          .then((res) => setSelected(res.data))
          .catch(() => {});
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pages, params]);
  useEffect(() => {
    const query = selected ? `?kind=${segment}&entity=${selected.id}` : `?kind=${segment}`;
    router.replace(`/dashboard/ecosystem/catalog${query}`);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [segment, selected]);
  const corroboration = useQuery({
    queryKey: ["eco-corroboration", segment, selected?.id],
    enabled: Boolean(selected),
    queryFn: () =>
      apiWithAuth<{ data: Corroboration }>(
        `/ecosystem/catalog/${segment}/${selected!.id}/corroboration`,
      ),
  });
  const scoreHistory = useQuery({
    queryKey: ["eco-score-history", segment, selected?.id],
    enabled: Boolean(selected),
    queryFn: () =>
      apiWithAuth<{ data: ScoreHistory }>(
        `/ecosystem/benchmark/score-history?entity_kind=${SEGMENT_TO_KIND[segment] ?? "model"}&entity_id=${selected!.id}`,
      ),
  });
  const priceHistory = useQuery({
    queryKey: ["eco-price-history", segment, selected?.id],
    enabled: Boolean(selected),
    queryFn: () =>
      apiWithAuth<{ data: PriceHistory }>(
        `/ecosystem/pricing/history?entity_kind=${SEGMENT_TO_KIND[segment] ?? "model"}&entity_id=${selected!.id}`,
      ),
  });
  const uptime = useQuery({
    queryKey: ["eco-uptime", segment, selected?.id],
    enabled: Boolean(selected),
    queryFn: () =>
      apiWithAuth<{ data: { current_status: string; uptime_pct: number | null } }>(
        `/ecosystem/pricing/availability/uptime?entity_kind=${SEGMENT_TO_KIND[segment] ?? "model"}&entity_id=${selected!.id}`,
      ),
  });
  const scorecard = useQuery({
    queryKey: ["eco-scorecard", segment, selected?.id],
    enabled: Boolean(selected),
    queryFn: () =>
      apiWithAuth<{ data: Scorecard }>(`/ecosystem/catalog/${segment}/${selected!.id}/scorecard`),
  });
  const [watched, setWatched] = useState<Set<string>>(new Set());
  const quickWatch = useMutation({
    mutationFn: (entityId: string) =>
      apiWithAuth("/ecosystem/watchlists/quick-watch", {
        method: "POST",
        body: JSON.stringify({
          target_kind: SEGMENT_TO_KIND[segment] ?? "model",
          target_id: entityId,
        }),
      }),
    onSuccess: (_res, entityId) => {
      setError(null);
      setWatched((prev) => new Set(prev).add(entityId));
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Watch failed"),
  });
  const [showDuplicates, setShowDuplicates] = useState(false);
  const duplicates = useQuery({
    queryKey: ["eco-duplicates", segment],
    enabled: showDuplicates,
    queryFn: () =>
      apiWithAuth<{ data: DuplicatePair[] }>(`/ecosystem/catalog/${segment}/duplicates`),
  });
  const [mergeTarget, setMergeTarget] = useState("");
  const mergeEntity = useMutation({
    mutationFn: () =>
      apiWithAuth(`/ecosystem/catalog/${segment}/${selected!.id}/merge-into/${mergeTarget}`, {
        method: "POST",
      }),
    onSuccess: () => {
      setError(null);
      setSelected(null);
      queryClient.invalidateQueries({ queryKey: ["eco-catalog", segment] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Merge failed"),
  });
  const resolveConflict = useMutation({
    mutationFn: ({ field, value }: { field: string; value: string }) =>
      apiWithAuth(`/ecosystem/catalog/${segment}/${selected!.id}/resolve-conflict`, {
        method: "POST",
        body: JSON.stringify({ field, chosen_value: value }),
      }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["eco-conflicts"] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Arbitration failed"),
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

  const rows = pages.length > 0 ? pages.flat() : (data?.data ?? []);

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
      <div>
        <button
          onClick={() => setShowDuplicates(!showDuplicates)}
          className="rounded-md border px-3 py-1 text-xs hover:bg-[hsl(var(--secondary))]"
        >
          {showDuplicates ? "Hide suspected duplicates" : "Scan for duplicates"}
        </button>
        {showDuplicates && (
          <div className="mt-2 space-y-2">
            {(duplicates.data?.data ?? []).length === 0 ? (
              <div className="text-xs text-[hsl(var(--muted-foreground))]">
                {duplicates.isLoading ? "Scanning…" : "No suspected duplicates."}
              </div>
            ) : (
              (duplicates.data?.data ?? []).map((d) => (
                <div
                  key={`${d.a.id}-${d.b.id}`}
                  className="flex flex-wrap items-center gap-2 rounded-md border bg-[hsl(var(--card))] p-2 text-xs"
                >
                  <span className="font-medium">{d.a.canonical_name}</span>
                  <span className="text-[hsl(var(--muted-foreground))]">≈</span>
                  <span className="font-medium">{d.b.canonical_name}</span>
                  <span className="text-[hsl(var(--muted-foreground))]">
                    similarity {d.similarity}
                  </span>
                  <span className="text-[hsl(var(--muted-foreground))]">
                    — inspect &amp; merge manually (merges are audited)
                  </span>
                </div>
              ))
            )}
          </div>
        )}
      </div>
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
                      aria-label="Lifecycle transition"
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
                    <button
                      title="Watch: get notified about changes to this entity"
                      onClick={() => quickWatch.mutate(entity.id)}
                      disabled={watched.has(entity.id)}
                      className="ml-2 rounded-md border px-2 py-1 text-xs hover:bg-[hsl(var(--secondary))] disabled:opacity-60"
                    >
                      {watched.has(entity.id) ? "✓ Watching" : "👁 Watch"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex items-center justify-between border-t px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
            <span>
              {rows.length} of {total}
            </span>
            {rows.length < total && (
              <button
                onClick={() => setOffset(rows.length)}
                className="rounded-md border px-3 py-1 hover:bg-[hsl(var(--secondary))]"
              >
                Load more
              </button>
            )}
          </div>
        </div>
      )}
      {selected && (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-semibold">
              {selected.canonical_name}
              {uptime.data?.data && (
                <span
                  title="Latest availability probe (probes run automatically for watched entities)"
                  className={`ml-2 rounded-full px-2 py-0.5 text-xs ${
                    {
                      operational: "bg-emerald-100 text-emerald-700",
                      degraded: "bg-amber-100 text-amber-800",
                      unreachable: "bg-red-100 text-red-700",
                    }[uptime.data.data.current_status] ?? "bg-slate-100 text-slate-600"
                  }`}
                >
                  {uptime.data.data.current_status}
                </span>
              )}
            </span>
            <span className="space-x-3">
              <Link
                href={`/dashboard/ecosystem/changes?entity=${selected.id}`}
                className="text-xs text-blue-600 underline"
              >
                📰 view changes
              </Link>
              <a
                href={`/api/v1/ecosystem/export/changes.atom?entity_id=${selected.id}`}
                className="text-xs text-blue-600 underline"
                title="Atom feed of changes to THIS entity (GitHub releases.atom posture)"
              >
                📡 subscribe (.atom)
              </a>
              <button
                aria-label="Close inspect panel"
                onClick={() => setSelected(null)}
                className="rounded-md border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
              >
                ✕ close
              </button>
            </span>
          </div>
          {scorecard.data?.data && (
            <div className="mb-3 space-y-2">
              <div className="flex items-center gap-2 text-sm font-semibold">
                Scorecard: {scorecard.data.data.grade} ({scorecard.data.data.passing}/
                {scorecard.data.data.applicable} checks passing)
              </div>
              <div className="flex flex-wrap gap-2">
                {scorecard.data.data.checks.map((c) => (
                  <span
                    key={c.check}
                    title={JSON.stringify(c.evidence)}
                    className={`rounded-full px-2 py-0.5 text-xs ${CHECK_STYLES[c.status] ?? ""}`}
                  >
                    {c.check}: {c.status}
                  </span>
                ))}
              </div>
            </div>
          )}
          {scoreHistory.data?.data && scoreHistory.data.data.points.length > 0 && (
            <div className="mb-3 flex flex-wrap items-center gap-2 text-xs">
              <span className="font-semibold">Benchmark reliability:</span>
              <span className="rounded-full border px-2 py-0.5">
                {scoreHistory.data.data.points[scoreHistory.data.data.points.length - 1]?.value}
                {scoreHistory.data.data.trend &&
                  (scoreHistory.data.data.trend.slope > 0
                    ? " ↑ improving"
                    : scoreHistory.data.data.trend.slope < 0
                      ? " ↓ declining"
                      : " → stable")}
                {" · "}
                {scoreHistory.data.data.points.length} runs
              </span>
            </div>
          )}
          {priceHistory.data?.data && Object.keys(priceHistory.data.data.series).length > 0 && (
            <div className="mb-3 flex flex-wrap gap-2 text-xs">
              <span className="font-semibold">Price trends:</span>
              {Object.entries(priceHistory.data.data.trends).map(([unit, t]) => {
                const pts = priceHistory.data!.data.series[unit] ?? [];
                const last = pts[pts.length - 1];
                return (
                  <span key={unit} className="rounded-full border px-2 py-0.5">
                    {unit}: {last ? `${last.price} ${last.currency}` : "—"}{" "}
                    {t ? (t.slope < 0 ? "↓ falling" : t.slope > 0 ? "↑ rising" : "→ flat") : ""}
                    {t && ` (proj. ${t.projected_next})`}
                  </span>
                );
              })}
            </div>
          )}
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-semibold">
              Source conflicts for {selected.canonical_name}
            </h3>
            {corroboration.data?.data && (
              <span className="text-xs text-[hsl(var(--muted-foreground))]">
                corroboration: {corroboration.data.data.distinct_sources} sources · trust score{" "}
                {corroboration.data.data.trust_weighted_score}
                {corroboration.data.data.human_verified_any ? " · human-verified" : ""}
              </span>
            )}
          </div>
          <div className="mt-2 flex gap-2">
            <input
              placeholder="merge into entity id (26 chars)…"
              value={mergeTarget}
              onChange={(e) => setMergeTarget(e.target.value)}
              className="flex-1 rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
            />
            <button
              onClick={() => mergeTarget.length === 26 && mergeEntity.mutate()}
              disabled={mergeTarget.length !== 26 || mergeEntity.isPending}
              className="rounded-md border px-2 py-1 text-xs disabled:opacity-50"
            >
              Merge duplicate → survivor
            </button>
          </div>
          {(conflicts.data?.data ?? []).length === 0 ? (
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              No disagreeing sources — all observations align.
            </p>
          ) : (
            <ul className="mt-2 space-y-2 text-sm">
              {(conflicts.data?.data ?? []).map((c) => (
                <li key={c.field} className="rounded-md border border-amber-300 bg-amber-50 p-3">
                  <span className="font-medium">{c.field}</span>: sources disagree
                  <div className="mt-1 flex flex-wrap gap-2">
                    {Object.entries(c.values).map(([value, sources]) => (
                      <button
                        key={value}
                        onClick={() => resolveConflict.mutate({ field: c.field, value })}
                        className={`rounded-md border px-2 py-0.5 text-xs hover:bg-white ${
                          c.curated?.value === value ? "border-emerald-600 font-semibold" : ""
                        }`}
                        title="Adopt this value as the curated decision"
                      >
                        &quot;{value}&quot; · {sources.length} src
                        {c.curated?.value === value ? " ✓ curated" : ""}
                      </button>
                    ))}
                  </div>
                  <div className="mt-1 text-xs text-amber-700">
                    Both observations stay retained; your pick becomes a curated overlay with
                    provenance.
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
