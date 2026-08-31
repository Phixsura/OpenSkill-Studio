"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Input } from "@/components/ui/input";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth } from "@/lib/api";
import { formatDate, formatMinor } from "@/lib/cp";

interface OpsInvoiceLine {
  id: string;
  line_type: string;
  description: string;
  amount_minor: number;
}

interface OpsInvoice {
  id: string;
  number: string | null;
  tenant_id: string;
  status: string;
  currency: string;
  total_minor: number;
  amount_due_minor: number;
  issued_at: string | null;
  lines: OpsInvoiceLine[];
}

interface TraceRated {
  id: string;
  usage_type: string;
  quantity: string;
  billable_amount_minor: number;
  billable_currency: string;
  internal_cost_minor: number;
  internal_cost_currency: string;
  margin_minor: number | null;
  cost_rate_snapshot: Record<string, unknown>;
  sell_rate_snapshot: Record<string, unknown>;
  fx_rate_snapshot: Record<string, unknown> | null;
  usage_event: {
    id: string;
    usage_type: string;
    quantity: string;
    occurred_at: string;
    source: string;
    refs: Record<string, string | null>;
  } | null;
}

interface Trace {
  line: { id: string; line_type: string; description: string; amount_minor: number };
  invoice: { id: string; number: string | null; tenant_id: string } | null;
  rated_usage: TraceRated[];
  counts: { rated_rows: number };
}

export default function PlatformInvoicesPage() {
  const [tenantId, setTenantId] = useState("");
  const [traceLineId, setTraceLineId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["platform-invoices", tenantId],
    queryFn: () => {
      const params = new URLSearchParams();
      if (tenantId) params.set("tenant_id", tenantId);
      return apiWithAuth<{ data: OpsInvoice[] }>(`/platform/invoices?${params.toString()}`);
    },
  });
  const invoices = data?.data ?? [];

  return (
    <div className="space-y-4">
      <Input
        className="max-w-xs"
        placeholder="Filter by tenant ID"
        value={tenantId}
        onChange={(e) => setTenantId(e.target.value)}
      />
      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
      <div className="space-y-3">
        {invoices.map((inv) => (
          <details key={inv.id} className="rounded-lg border p-4">
            <summary className="flex cursor-pointer flex-wrap items-center gap-3 text-sm">
              <span className="font-mono">{inv.number ?? inv.id.slice(0, 12)}</span>
              <StatusBadge status={inv.status} />
              <span className="font-mono text-xs text-[hsl(var(--muted-foreground))]">
                {inv.tenant_id.slice(0, 10)}…
              </span>
              <span className="ml-auto font-mono">
                {formatMinor(inv.total_minor, inv.currency)}
              </span>
              <span className="text-xs text-[hsl(var(--muted-foreground))]">
                {formatDate(inv.issued_at)}
              </span>
            </summary>
            <table className="mt-3 w-full text-sm">
              <tbody>
                {inv.lines.map((line) => (
                  <tr key={line.id} className="border-b last:border-0">
                    <td className="py-1.5">
                      <span className="mr-2 rounded bg-[hsl(var(--secondary))] px-1.5 py-0.5 text-xs">
                        {line.line_type}
                      </span>
                      {line.description}
                    </td>
                    <td className="py-1.5 text-right font-mono">
                      {formatMinor(line.amount_minor, inv.currency)}
                    </td>
                    <td className="py-1.5 pl-3 text-right">
                      {line.line_type === "usage" && (
                        <button
                          className="rounded-md border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
                          onClick={() => setTraceLineId(line.id)}
                        >
                          Trace
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </details>
        ))}
      </div>

      {traceLineId && <TraceDrawer lineId={traceLineId} onClose={() => setTraceLineId(null)} />}
    </div>
  );
}

/** §37 acceptance UI: invoice line → RatedUsage snapshots → provider call refs. */
function TraceDrawer({ lineId, onClose }: { lineId: string; onClose: () => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ["trace-invoice-line", lineId],
    queryFn: () => apiWithAuth<{ data: Trace }>(`/platform/trace/invoice-lines/${lineId}`),
  });
  const trace = data?.data;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/50" onClick={onClose}>
      <div
        className="h-full w-full max-w-2xl overflow-y-auto border-l bg-[hsl(var(--card))] p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Billing trace</h2>
          <button className="rounded-md border px-3 py-1 text-sm" onClick={onClose}>
            Close
          </button>
        </div>
        {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
        {trace && (
          <div className="space-y-4 text-sm">
            <div className="rounded-md border p-3">
              <p className="font-medium">{trace.line.description}</p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                Invoice {trace.invoice?.number ?? trace.invoice?.id} · {trace.counts.rated_rows}{" "}
                rated rows
              </p>
            </div>
            {trace.rated_usage.map((r) => (
              <details key={r.id} className="rounded-md border p-3" open>
                <summary className="cursor-pointer">
                  <span className="font-mono text-xs">{r.usage_type}</span> · qty {r.quantity} ·
                  billable {formatMinor(r.billable_amount_minor, r.billable_currency)} · cost{" "}
                  {formatMinor(r.internal_cost_minor, r.internal_cost_currency)} · margin{" "}
                  {r.margin_minor != null ? formatMinor(r.margin_minor, "USD") : "—"}
                </summary>
                <div className="mt-2 space-y-2">
                  {r.usage_event && (
                    <div className="rounded bg-[hsl(var(--secondary))] p-2 text-xs">
                      <p className="font-medium">Provider call</p>
                      <p>
                        {r.usage_event.refs.provider ?? "—"} /{" "}
                        {r.usage_event.refs.model_or_service ?? "—"} ·{" "}
                        {new Date(r.usage_event.occurred_at).toLocaleString()} · source{" "}
                        {r.usage_event.source}
                      </p>
                      {r.usage_event.refs.workflow_run_id && (
                        <p className="font-mono">run {r.usage_event.refs.workflow_run_id}</p>
                      )}
                      {r.usage_event.refs.evaluation_task_id && (
                        <p className="font-mono">eval {r.usage_event.refs.evaluation_task_id}</p>
                      )}
                    </div>
                  )}
                  <SnapshotBlock title="Cost rate snapshot" data={r.cost_rate_snapshot} />
                  <SnapshotBlock title="Sell rate snapshot" data={r.sell_rate_snapshot} />
                  {r.fx_rate_snapshot && (
                    <SnapshotBlock title="FX snapshot" data={r.fx_rate_snapshot} />
                  )}
                </div>
              </details>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function SnapshotBlock({ title, data }: { title: string; data: Record<string, unknown> }) {
  return (
    <details className="text-xs">
      <summary className="cursor-pointer text-[hsl(var(--muted-foreground))]">{title}</summary>
      <pre className="mt-1 max-h-40 overflow-auto rounded bg-[hsl(var(--secondary))] p-2">
        {JSON.stringify(data, null, 2)}
      </pre>
    </details>
  );
}
