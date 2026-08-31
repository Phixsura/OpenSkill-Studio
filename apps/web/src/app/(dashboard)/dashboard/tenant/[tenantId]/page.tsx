"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth } from "@/lib/api";
import { formatDate, type TenantEntitlements } from "@/lib/cp";

interface TenantDetail {
  id: string;
  name: string;
  slug: string;
  status: string;
  account_type: string;
  currency: string;
  timezone: string;
  billing_email: string | null;
  trial_ends_at: string | null;
  created_at: string;
}

export default function TenantOverviewPage() {
  const { tenantId } = useParams<{ tenantId: string }>();

  const tenantQuery = useQuery({
    queryKey: ["tenant", tenantId],
    queryFn: () => apiWithAuth<{ data: TenantDetail }>(`/tenants/${tenantId}`),
  });
  const entQuery = useQuery({
    queryKey: ["tenant-entitlements", tenantId],
    queryFn: () => apiWithAuth<{ data: TenantEntitlements }>(`/tenants/${tenantId}/entitlements`),
  });

  const tenant = tenantQuery.data?.data;
  const ent = entQuery.data?.data;

  if (tenantQuery.isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (tenantQuery.isError || !tenant) {
    return <p className="text-sm text-red-600">Failed to load tenant.</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-3xl font-bold">{tenant.name}</h1>
        <StatusBadge status={tenant.status} />
      </div>

      {tenant.status === "trial" && tenant.trial_ends_at && (
        <div className="rounded-md border border-blue-300 bg-blue-50 px-4 py-3 text-sm text-blue-900 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-100">
          Trial ends {formatDate(tenant.trial_ends_at)} — subscribe on the Billing tab to keep your
          plan entitlements.
        </div>
      )}
      {tenant.status === "suspended" && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100">
          This account is suspended: new runs, evaluations, uploads and purchases are blocked. Data
          remains readable. Contact support or settle outstanding invoices to reactivate.
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <InfoCard label="Plan" value={ent?.plan ? `${ent.plan.key} v${ent.plan.version}` : "—"} />
        <InfoCard label="Currency" value={tenant.currency} />
        <InfoCard label="Timezone" value={tenant.timezone} />
        <InfoCard label="Billing email" value={tenant.billing_email ?? "—"} />
      </div>

      <div>
        <h2 className="mb-3 text-lg font-semibold">Entitlements & usage</h2>
        {entQuery.isLoading && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
        )}
        {ent && (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Entitlement</th>
                  <th className="px-4 py-2 font-medium">Limit</th>
                  <th className="px-4 py-2 font-medium">Usage</th>
                  <th className="px-4 py-2 font-medium">Source</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(ent.entitlements).map(([key, entry]) => (
                  <tr key={key} className="border-b last:border-0">
                    <td className="px-4 py-2 font-mono text-xs">{key}</td>
                    <td className="px-4 py-2">
                      {entry.value === null
                        ? "unlimited"
                        : typeof entry.value === "boolean"
                          ? entry.value
                            ? "✓"
                            : "✗"
                          : String(entry.value)}
                    </td>
                    <td className="px-4 py-2">
                      {entry.usage !== undefined && entry.usage !== null
                        ? String(entry.usage)
                        : "—"}
                    </td>
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
                      {entry.source}
                      {entry.enforcement === "soft" ? " (soft)" : ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border p-4">
      <p className="text-xs text-[hsl(var(--muted-foreground))]">{label}</p>
      <p className="mt-1 truncate font-medium">{value}</p>
    </div>
  );
}
