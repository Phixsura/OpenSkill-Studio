"use client";
/** Side-by-side entity comparison + workload cost estimator (ADR-016 §19). */

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill } from "../components";
import { LIFECYCLE_STYLES } from "../lib";

interface PriceEntry {
  unit: string;
  price: number;
  currency: string;
  approved: boolean;
}

interface CompareRow {
  entity_kind: string;
  entity_id: string;
  canonical_name: string;
  lifecycle_status: string;
  prices: Record<string, PriceEntry>;
  availability_status: Record<string, unknown> | null;
  benchmark: {
    run_id: string;
    finished_at: string | null;
    dimension_scores: Record<string, number>;
  } | null;
}

interface EstimateRow {
  entity_id: string;
  estimated_total: number | null;
  currency: string | null;
  fully_priced: boolean;
  all_prices_approved: boolean;
  missing_units: string[];
  breakdown: {
    unit: string;
    quantity: number;
    unit_price: number;
    line_total: number;
    approved: boolean;
  }[];
}

const KINDS = ["provider", "tool", "model", "model_version", "workflow", "agent", "node_package"];

export default function ComparePage() {
  return (
    <Suspense>
      <CompareInner />
    </Suspense>
  );
}

function CompareInner() {
  const router = useRouter();
  const params = useSearchParams();
  const [kind, setKind] = useState(params.get("kind") ?? "model");
  const [ids, setIds] = useState(params.get("ids") ?? "");
  const [submitted, setSubmitted] = useState<{ kind: string; ids: string } | null>(
    params.get("ids") ? { kind: params.get("kind") ?? "model", ids: params.get("ids")! } : null,
  );
  // Shareable URLs: the comparison lives in the querystring
  useEffect(() => {
    if (submitted) {
      router.replace(
        `/dashboard/ecosystem/compare?kind=${submitted.kind}&ids=${encodeURIComponent(submitted.ids)}`,
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [submitted]);
  const [workload, setWorkload] = useState('{"token_input": 1000000, "token_output": 200000}');
  const [estimate, setEstimate] = useState<EstimateRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["eco-compare", submitted],
    enabled: submitted !== null,
    queryFn: () =>
      apiWithAuth<{ data: CompareRow[] }>(
        `/ecosystem/compare?kind=${submitted!.kind}&ids=${encodeURIComponent(submitted!.ids)}`,
      ),
  });

  const rows = data?.data ?? [];
  const allUnits = Array.from(new Set(rows.flatMap((r) => Object.keys(r.prices)))).sort();
  const allDims = Array.from(
    new Set(rows.flatMap((r) => Object.keys(r.benchmark?.dimension_scores ?? {}))),
  ).sort();

  const runEstimate = async () => {
    setError(null);
    setEstimate(null);
    try {
      const parsed = JSON.parse(workload) as Record<string, number>;
      const entityIds = ids
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const res = await apiWithAuth<{ data: EstimateRow[] }>(`/ecosystem/pricing/estimate`, {
        method: "POST",
        body: JSON.stringify({ entity_kind: kind, entity_ids: entityIds, workload: parsed }),
      });
      setEstimate(res.data);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Invalid workload JSON or request failed");
    }
  };

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Compare &amp; Estimate</h1>
      <EcosystemNav />
      <p className="text-sm text-[hsl(var(--muted-foreground))]">
        Side-by-side facts, prices, availability and benchmark scores. Cost estimates are advisory —
        never billing quotes; unpriced units are flagged, not zeroed.
      </p>
      <div className="flex flex-wrap items-center gap-3">
        <select
          aria-label="Entity kind"
          value={kind}
          onChange={(e) => setKind(e.target.value)}
          className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
        >
          {KINDS.map((k) => (
            <option key={k}>{k}</option>
          ))}
        </select>
        <input
          placeholder="entity ids, comma-separated (2-6)"
          value={ids}
          onChange={(e) => setIds(e.target.value)}
          className="w-96 rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
        />
        <button
          onClick={() => setSubmitted({ kind, ids })}
          className="rounded-md bg-[hsl(var(--primary))] px-3 py-2 text-sm text-[hsl(var(--primary-foreground))]"
        >
          Compare
        </button>
      </div>

      {isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Comparing…</div>
      ) : rows.length === 0 && submitted ? (
        <EmptyState icon="⚖️" text="Nothing to compare yet." />
      ) : rows.length > 0 ? (
        <div className="overflow-x-auto rounded-lg border shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-[hsl(var(--secondary))]">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Attribute</th>
                {rows.map((r) => (
                  <th key={r.entity_id} className="px-4 py-3 text-left font-medium">
                    {r.canonical_name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="bg-[hsl(var(--card))]">
                <td className="px-4 py-2 font-medium">Lifecycle</td>
                {rows.map((r) => (
                  <td key={r.entity_id} className="px-4 py-2">
                    <Pill value={r.lifecycle_status} styles={LIFECYCLE_STYLES} />
                  </td>
                ))}
              </tr>
              {allUnits.map((unit) => (
                <tr key={unit} className="bg-[hsl(var(--card))]">
                  <td className="px-4 py-2 font-medium">Price / {unit}</td>
                  {rows.map((r) => {
                    const p = r.prices[unit];
                    return (
                      <td key={r.entity_id} className="px-4 py-2">
                        {p ? (
                          <>
                            {p.price} {p.currency}{" "}
                            {p.approved ? (
                              <span className="text-xs text-emerald-600">✓ approved</span>
                            ) : (
                              <span className="text-xs text-amber-600">observed</span>
                            )}
                          </>
                        ) : (
                          "—"
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
              {allDims.map((dim) => (
                <tr key={dim} className="bg-[hsl(var(--card))]">
                  <td className="px-4 py-2 font-medium">Benchmark · {dim}</td>
                  {rows.map((r) => (
                    <td key={r.entity_id} className="px-4 py-2">
                      {r.benchmark?.dimension_scores[dim] ?? "—"}
                    </td>
                  ))}
                </tr>
              ))}
              <tr className="bg-[hsl(var(--card))]">
                <td className="px-4 py-2 font-medium">Availability</td>
                {rows.map((r) => (
                  <td key={r.entity_id} className="px-4 py-2 font-mono text-xs">
                    {r.availability_status ? JSON.stringify(r.availability_status) : "—"}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      ) : null}

      <div className="space-y-3 rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
        <h2 className="font-semibold">Workload cost estimator</h2>
        <textarea
          value={workload}
          onChange={(e) => setWorkload(e.target.value)}
          rows={2}
          className="w-full rounded-md border bg-[hsl(var(--background))] px-3 py-2 font-mono text-xs"
        />
        <button
          onClick={runEstimate}
          className="rounded-md border px-3 py-2 text-sm hover:bg-[hsl(var(--secondary))]"
        >
          Estimate cost
        </button>
        {error && (
          <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </div>
        )}
        {estimate && (
          <div className="space-y-2">
            {estimate.map((e) => (
              <div key={e.entity_id} className="rounded-md border p-3 text-sm">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs">{e.entity_id.slice(0, 12)}…</span>
                  <span className="font-semibold">
                    {e.estimated_total !== null
                      ? `${e.estimated_total} ${e.currency ?? ""}`
                      : "no priced units"}
                  </span>
                  {!e.fully_priced && (
                    <span className="text-xs text-amber-600">
                      missing: {e.missing_units.join(", ")}
                    </span>
                  )}
                  {e.all_prices_approved && (
                    <span className="text-xs text-emerald-600">all approved</span>
                  )}
                </div>
                <div className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                  {e.breakdown
                    .map((b) => `${b.unit}: ${b.quantity} × ${b.unit_price} = ${b.line_total}`)
                    .join(" · ")}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
