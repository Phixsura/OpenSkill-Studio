"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Input } from "@/components/ui/input";
import { apiWithAuth } from "@/lib/api";

interface UsageEvent {
  id: string;
  tenant_id: string;
  org_id: string;
  usage_type: string;
  quantity: string;
  unit: string;
  provider: string | null;
  model_or_service: string | null;
  source: string;
  occurred_at: string;
}

export default function PlatformUsagePage() {
  const [tenantId, setTenantId] = useState("");
  const [usageType, setUsageType] = useState("");
  const [source, setSource] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["platform-usage", tenantId, usageType, source, page],
    queryFn: () => {
      const params = new URLSearchParams({ page: String(page) });
      if (tenantId) params.set("tenant_id", tenantId);
      if (usageType) params.set("usage_type", usageType);
      if (source) params.set("source", source);
      return apiWithAuth<{ data: UsageEvent[]; meta: { total: number; has_more: boolean } }>(
        `/platform/usage-events?${params.toString()}`,
      );
    },
  });
  const events = data?.data ?? [];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Input
          className="max-w-xs"
          placeholder="Tenant ID"
          value={tenantId}
          onChange={(e) => {
            setTenantId(e.target.value);
            setPage(1);
          }}
        />
        <Input
          className="max-w-[14rem]"
          placeholder="Usage type"
          value={usageType}
          onChange={(e) => {
            setUsageType(e.target.value);
            setPage(1);
          }}
        />
        <Input
          className="max-w-[12rem]"
          placeholder="Source"
          value={source}
          onChange={(e) => {
            setSource(e.target.value);
            setPage(1);
          }}
        />
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
      {!isLoading && (
        <>
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Occurred</th>
                  <th className="px-4 py-2 font-medium">Tenant</th>
                  <th className="px-4 py-2 font-medium">Type</th>
                  <th className="px-4 py-2 text-right font-medium">Qty</th>
                  <th className="px-4 py-2 font-medium">Provider</th>
                  <th className="px-4 py-2 font-medium">Source</th>
                </tr>
              </thead>
              <tbody>
                {events.map((e) => (
                  <tr key={e.id} className="border-b last:border-0">
                    <td className="px-4 py-2 text-xs">
                      {new Date(e.occurred_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-2 font-mono text-xs">{e.tenant_id.slice(0, 10)}…</td>
                    <td className="px-4 py-2 font-mono text-xs">{e.usage_type}</td>
                    <td className="px-4 py-2 text-right font-mono">
                      {e.quantity} {e.unit}
                    </td>
                    <td className="px-4 py-2 text-xs">
                      {e.provider ?? "—"}
                      {e.model_or_service ? ` / ${e.model_or_service}` : ""}
                    </td>
                    <td className="px-4 py-2 text-xs">{e.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <button
              className="rounded-md border px-3 py-1 disabled:opacity-40"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Prev
            </button>
            <span>Page {page}</span>
            <button
              className="rounded-md border px-3 py-1 disabled:opacity-40"
              onClick={() => setPage((p) => p + 1)}
              disabled={!data?.meta.has_more}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
