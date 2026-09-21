"use client";
/** Pricing observations + reconciliation into the billing catalog (Part E). */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill } from "../components";
import { STATUS_STYLES, fmtDate } from "../lib";

interface PriceObservation {
  id: string;
  entity_kind: string;
  entity_id: string;
  region: string | null;
  unit: string;
  price: number;
  currency: string;
  observed_at: string;
  reconciliation_status: string;
  approved_cost_rate_id: string | null;
}

export default function PricingPage() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("unreviewed");
  const [error, setError] = useState<string | null>(null);
  const [providerKey, setProviderKey] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["eco-pricing", status],
    queryFn: () =>
      apiWithAuth<{ data: PriceObservation[] }>(
        `/ecosystem/pricing/observations?limit=100${status ? `&reconciliation_status=${status}` : ""}`,
      ),
  });

  const reconcile = useMutation({
    mutationFn: ({ id, decision }: { id: string; decision: string }) =>
      apiWithAuth(`/ecosystem/pricing/observations/${id}/reconcile`, {
        method: "POST",
        body: JSON.stringify({
          decision,
          provider_key: decision === "approve" ? providerKey || null : null,
        }),
      }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["eco-pricing"] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Reconciliation failed"),
  });

  const rows = data?.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Pricing Intelligence</h1>
      <EcosystemNav />
      <p className="text-sm text-[hsl(var(--muted-foreground))]">
        Observed external prices never rewrite billing. Approving mints a NEW cost rate in the
        control-plane catalog, effective from now.
      </p>
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
        >
          <option value="">All statuses</option>
          {["unreviewed", "under_review", "approved", "rejected", "superseded"].map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        <input
          placeholder="provider key for approval (e.g. openai)"
          value={providerKey}
          onChange={(e) => setProviderKey(e.target.value)}
          className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
        />
      </div>
      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}
      {isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading price observations…</div>
      ) : rows.length === 0 ? (
        <EmptyState icon="💱" text="No price observations in this state." />
      ) : (
        <div className="overflow-x-auto rounded-lg border shadow-sm">
          <table className="w-full">
            <thead className="bg-[hsl(var(--secondary))]">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Entity</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Unit</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Price</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Observed</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {rows.map((p) => (
                <tr key={p.id} className="bg-[hsl(var(--card))]">
                  <td className="px-4 py-3 text-sm">
                    {p.entity_kind}
                    <div className="font-mono text-xs text-[hsl(var(--muted-foreground))]">
                      {p.entity_id.slice(0, 10)}…
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {p.unit}
                    {p.region ? ` (${p.region})` : ""}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium">
                    {Number(p.price).toFixed(4)} {p.currency}
                  </td>
                  <td className="px-4 py-3 text-sm text-[hsl(var(--muted-foreground))]">
                    {fmtDate(p.observed_at)}
                  </td>
                  <td className="px-4 py-3">
                    <Pill value={p.reconciliation_status} styles={STATUS_STYLES} />
                  </td>
                  <td className="space-x-2 px-4 py-3">
                    {["unreviewed", "under_review"].includes(p.reconciliation_status) && (
                      <>
                        <button
                          onClick={() => reconcile.mutate({ id: p.id, decision: "approve" })}
                          className="rounded-md bg-emerald-600 px-2 py-1 text-xs text-white"
                        >
                          Approve → billing
                        </button>
                        <button
                          onClick={() => reconcile.mutate({ id: p.id, decision: "reject" })}
                          className="rounded-md border px-2 py-1 text-xs"
                        >
                          Reject
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
