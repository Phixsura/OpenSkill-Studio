"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { cn } from "@/lib/utils";
import { apiWithAuth } from "@/lib/api";
import { formatDate } from "@/lib/cp";

interface CostRate {
  id: string;
  provider: string;
  model_or_service: string | null;
  usage_type: string;
  currency: string;
  unit_cost: string;
  effective_from: string;
  effective_until: string | null;
}

interface PricePolicy {
  id: string;
  name: string;
  policy_type: string;
  usage_type: string | null;
  tenant_id: string | null;
  partner_id: string | null;
  plan_version_id: string | null;
  currency: string;
  params: Record<string, unknown>;
  is_active: boolean;
  effective_from: string;
}

interface FxRate {
  id: string;
  base_currency: string;
  quote_currency: string;
  rate: string;
  effective_from: string;
  effective_until: string | null;
}

const TABS = ["cost-rates", "price-policies", "fx-rates"] as const;

export default function PlatformPricingPage() {
  const [tab, setTab] = useState<(typeof TABS)[number]>("cost-rates");

  return (
    <div className="space-y-4">
      <div className="flex gap-1">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm",
              tab === t
                ? "bg-[hsl(var(--secondary))] font-medium"
                : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--secondary))]",
            )}
          >
            {t.replace("-", " ")}
          </button>
        ))}
      </div>
      {tab === "cost-rates" && <CostRatesTab />}
      {tab === "price-policies" && <PoliciesTab />}
      {tab === "fx-rates" && <FxTab />}
    </div>
  );
}

function CostRatesTab() {
  const { data, isLoading } = useQuery({
    queryKey: ["platform-cost-rates"],
    queryFn: () => apiWithAuth<{ data: CostRate[] }>("/platform/cost-rates"),
  });
  const rates = data?.data ?? [];
  if (isLoading) return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full text-sm">
        <thead className="border-b bg-[hsl(var(--secondary))] text-left">
          <tr>
            <th className="px-4 py-2 font-medium">Provider</th>
            <th className="px-4 py-2 font-medium">Model / service</th>
            <th className="px-4 py-2 font-medium">Usage type</th>
            <th className="px-4 py-2 text-right font-medium">Unit cost</th>
            <th className="px-4 py-2 font-medium">Window</th>
          </tr>
        </thead>
        <tbody>
          {rates.map((r) => (
            <tr key={r.id} className="border-b last:border-0">
              <td className="px-4 py-2">{r.provider}</td>
              <td className="px-4 py-2 font-mono text-xs">{r.model_or_service ?? "*"}</td>
              <td className="px-4 py-2 font-mono text-xs">{r.usage_type}</td>
              <td className="px-4 py-2 text-right font-mono">
                {r.unit_cost} {r.currency}
              </td>
              <td className="px-4 py-2 text-xs">
                {formatDate(r.effective_from)} →{" "}
                {r.effective_until ? formatDate(r.effective_until) : "open"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PoliciesTab() {
  const { data, isLoading } = useQuery({
    queryKey: ["platform-price-policies"],
    queryFn: () => apiWithAuth<{ data: PricePolicy[] }>("/platform/price-policies"),
  });
  const policies = data?.data ?? [];
  if (isLoading) return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full text-sm">
        <thead className="border-b bg-[hsl(var(--secondary))] text-left">
          <tr>
            <th className="px-4 py-2 font-medium">Name</th>
            <th className="px-4 py-2 font-medium">Type</th>
            <th className="px-4 py-2 font-medium">Scope</th>
            <th className="px-4 py-2 font-medium">Usage type</th>
            <th className="px-4 py-2 font-medium">Params</th>
          </tr>
        </thead>
        <tbody>
          {policies.map((p) => (
            <tr key={p.id} className={`border-b last:border-0 ${!p.is_active ? "opacity-50" : ""}`}>
              <td className="px-4 py-2">{p.name}</td>
              <td className="px-4 py-2 font-mono text-xs">{p.policy_type}</td>
              <td className="px-4 py-2 text-xs">
                {p.tenant_id
                  ? "tenant"
                  : p.partner_id
                    ? "partner"
                    : p.plan_version_id
                      ? "plan"
                      : "global"}
              </td>
              <td className="px-4 py-2 font-mono text-xs">{p.usage_type ?? "*"}</td>
              <td className="px-4 py-2 font-mono text-xs">{JSON.stringify(p.params)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function FxTab() {
  const { data, isLoading } = useQuery({
    queryKey: ["platform-fx-rates"],
    queryFn: () => apiWithAuth<{ data: FxRate[] }>("/platform/fx-rates"),
  });
  const rates = data?.data ?? [];
  if (isLoading) return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  if (rates.length === 0)
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">No FX rates.</p>;
  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full text-sm">
        <thead className="border-b bg-[hsl(var(--secondary))] text-left">
          <tr>
            <th className="px-4 py-2 font-medium">Pair</th>
            <th className="px-4 py-2 text-right font-medium">Rate</th>
            <th className="px-4 py-2 font-medium">Window</th>
          </tr>
        </thead>
        <tbody>
          {rates.map((r) => (
            <tr key={r.id} className="border-b last:border-0">
              <td className="px-4 py-2 font-mono">
                {r.base_currency}/{r.quote_currency}
              </td>
              <td className="px-4 py-2 text-right font-mono">{r.rate}</td>
              <td className="px-4 py-2 text-xs">
                {formatDate(r.effective_from)} →{" "}
                {r.effective_until ? formatDate(r.effective_until) : "open"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
