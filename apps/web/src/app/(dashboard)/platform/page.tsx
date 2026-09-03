"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

interface Dashboard {
  period: string;
  tenants: { by_status: Record<string, number>; total: number };
  mrr_minor: number;
  // R101[H5]: mrr_minor is only the platform-currency slice — the full book
  mrr_by_currency: Record<string, number>;
  usage: {
    by_type: {
      usage_type: string;
      // R101[H4]: rows are grouped per (type, billable_currency, cost_currency)
      currency: string;
      cost_currency: string;
      quantity: string;
      billable_minor: number;
      cost_minor: number;
      margin_minor: number | null;
    }[];
  };
  totals: {
    billable_minor: number;
    billable_by_currency: Record<string, number>;
    internal_cost_minor: number;
    cost_by_currency: Record<string, number>;
    margin_minor: number;
    unrated_events: number;
    blocked_rated: number;
  };
  credits_outstanding: { currency: string; balance_minor: number; reserved_minor: number }[];
  settlement_liabilities: { currency: string; accrued_minor: number }[];
  marketplace_gmv_minor: number;
  marketplace_gmv_by_currency: Record<string, number>;
  attention: {
    past_due: { tenant_id: string; name: string; slug: string }[];
    suspended: { tenant_id: string; name: string; slug: string }[];
    failed_webhooks: number;
    dead_outbox: number;
  };
}

/** Render a per-currency map ("$5,000.00 · ¥6,000,000"); platform currency first. */
function multiCurrency(map: Record<string, number> | undefined, fallback: string): string {
  const entries = Object.entries(map ?? {});
  if (entries.length === 0) return fallback;
  return entries
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([cur, minor]) => formatMinor(minor, cur))
    .join(" · ");
}

export default function PlatformDashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["platform-dashboard"],
    queryFn: () => apiWithAuth<{ data: Dashboard }>("/platform/dashboard"),
  });
  const d = data?.data;

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError || !d) {
    return <p className="text-sm text-red-600">Failed to load dashboard.</p>;
  }

  return (
    <div className="space-y-8">
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-bold">Platform dashboard</h1>
        <span className="text-sm text-[hsl(var(--muted-foreground))]">{d.period}</span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card
          label="MRR"
          value={multiCurrency(d.mrr_by_currency, formatMinor(d.mrr_minor, "USD"))}
        />
        <Card label="Tenants" value={String(d.tenants.total)} />
        <Card
          label="Billable (period)"
          value={multiCurrency(
            d.totals.billable_by_currency,
            formatMinor(d.totals.billable_minor, "USD"),
          )}
        />
        <Card
          label="Margin (period)"
          value={formatMinor(d.totals.margin_minor, "USD")}
          sub={`cost ${multiCurrency(d.totals.cost_by_currency, formatMinor(d.totals.internal_cost_minor, "USD"))}`}
        />
        <Card
          label="Marketplace GMV"
          value={multiCurrency(
            d.marketplace_gmv_by_currency,
            formatMinor(d.marketplace_gmv_minor, "USD"),
          )}
        />
        {/* R113[H6]: render EVERY currency — [0] hid all but one aggregate */}
        <Card
          label="Credits outstanding"
          value={
            d.credits_outstanding.length
              ? d.credits_outstanding
                  .map((c) => formatMinor(c.balance_minor, c.currency))
                  .join(" · ")
              : "—"
          }
        />
        <Card
          label="Settlement liability"
          value={
            d.settlement_liabilities.length
              ? d.settlement_liabilities
                  .map((s) => formatMinor(s.accrued_minor, s.currency))
                  .join(" · ")
              : "—"
          }
        />
        <Card
          label="Attention"
          value={`${d.attention.failed_webhooks + d.attention.dead_outbox + d.totals.blocked_rated}`}
          sub={`${d.attention.failed_webhooks} webhooks · ${d.attention.dead_outbox} outbox · ${d.totals.blocked_rated} blocked`}
          alert={d.attention.failed_webhooks + d.attention.dead_outbox + d.totals.blocked_rated > 0}
        />
      </div>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Tenants by status</h2>
        <div className="flex flex-wrap gap-3">
          {Object.entries(d.tenants.by_status).map(([status, count]) => (
            <div key={status} className="rounded-lg border px-4 py-2 text-sm">
              <span className="font-semibold">{count}</span>{" "}
              <span className="text-[hsl(var(--muted-foreground))]">{status}</span>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Usage economics (period)</h2>
        {d.usage.by_type.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No rated usage.</p>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Usage type</th>
                  <th className="px-4 py-2 text-right font-medium">Quantity</th>
                  <th className="px-4 py-2 text-right font-medium">Billable</th>
                  <th className="px-4 py-2 text-right font-medium">Cost</th>
                  <th className="px-4 py-2 text-right font-medium">Margin</th>
                </tr>
              </thead>
              <tbody>
                {d.usage.by_type.map((u) => (
                  <tr
                    key={`${u.usage_type}:${u.currency}:${u.cost_currency}`}
                    className="border-b last:border-0"
                  >
                    <td className="px-4 py-2 font-mono text-xs">{u.usage_type}</td>
                    <td className="px-4 py-2 text-right">{u.quantity}</td>
                    <td className="px-4 py-2 text-right font-mono">
                      {formatMinor(u.billable_minor, u.currency)}
                    </td>
                    <td className="px-4 py-2 text-right font-mono">
                      {formatMinor(u.cost_minor, u.cost_currency)}
                    </td>
                    <td className="px-4 py-2 text-right font-mono">
                      {u.margin_minor != null ? formatMinor(u.margin_minor, "USD") : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {(d.attention.past_due.length > 0 || d.attention.suspended.length > 0) && (
        <section>
          <h2 className="mb-3 text-lg font-semibold">Needs attention</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {d.attention.past_due.length > 0 && (
              <AttentionList title="Past due" items={d.attention.past_due} />
            )}
            {d.attention.suspended.length > 0 && (
              <AttentionList title="Suspended" items={d.attention.suspended} />
            )}
          </div>
        </section>
      )}
    </div>
  );
}

function Card({
  label,
  value,
  sub,
  alert,
}: {
  label: string;
  value: string;
  sub?: string;
  alert?: boolean;
}) {
  return (
    <div className={`rounded-lg border p-4 ${alert ? "border-amber-400" : ""}`}>
      <p className="text-xs text-[hsl(var(--muted-foreground))]">{label}</p>
      <p className="mt-1 text-xl font-bold">{value}</p>
      {sub && <p className="text-xs text-[hsl(var(--muted-foreground))]">{sub}</p>}
    </div>
  );
}

function AttentionList({
  title,
  items,
}: {
  title: string;
  items: { tenant_id: string; name: string; slug: string }[];
}) {
  return (
    <div className="rounded-lg border p-4">
      <p className="mb-2 text-sm font-semibold">{title}</p>
      <ul className="space-y-1 text-sm">
        {items.map((t) => (
          <li key={t.tenant_id}>
            <Link
              href={`/platform/tenants/${t.tenant_id}`}
              className="underline-offset-2 hover:underline"
            >
              {t.name}
            </Link>{" "}
            <span className="text-xs text-[hsl(var(--muted-foreground))]">({t.slug})</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
