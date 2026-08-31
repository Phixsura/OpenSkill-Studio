"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth } from "@/lib/api";
import { formatDate, formatMinor } from "@/lib/cp";

interface LicenseGrant {
  id: string;
  product_type: string;
  product_id: string;
  org_id: string | null;
  scope: string;
  seat_limit: number | null;
  status: string;
  source: string;
  starts_at: string;
  expires_at: string | null;
}

interface Purchase {
  id: string;
  listing_id: string;
  status: string;
  amount_minor: number;
  currency: string;
  payment_method: string | null;
  created_at: string;
}

export default function TenantLicensesPage() {
  const { tenantId } = useParams<{ tenantId: string }>();

  const licensesQuery = useQuery({
    queryKey: ["tenant-licenses", tenantId],
    queryFn: () => apiWithAuth<{ data: LicenseGrant[] }>(`/tenants/${tenantId}/licenses`),
  });
  const purchasesQuery = useQuery({
    queryKey: ["tenant-purchases", tenantId],
    queryFn: () => apiWithAuth<{ data: Purchase[] }>(`/tenants/${tenantId}/purchases`),
  });

  const licenses = licensesQuery.data?.data ?? [];
  const purchases = purchasesQuery.data?.data ?? [];

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-3 text-lg font-semibold">Licenses</h2>
        {licenses.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            No licenses. Purchase paid packs from the registry to license them here.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Product</th>
                  <th className="px-4 py-2 font-medium">Scope</th>
                  <th className="px-4 py-2 font-medium">Source</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Since</th>
                </tr>
              </thead>
              <tbody>
                {licenses.map((g) => (
                  <tr key={g.id} className="border-b last:border-0">
                    <td className="px-4 py-2">
                      <span className="rounded bg-[hsl(var(--secondary))] px-1.5 py-0.5 text-xs">
                        {g.product_type}
                      </span>{" "}
                      <span className="font-mono text-xs">{g.product_id.slice(0, 12)}…</span>
                    </td>
                    <td className="px-4 py-2">
                      {g.scope}
                      {g.seat_limit != null ? ` (${g.seat_limit} seats)` : ""}
                    </td>
                    <td className="px-4 py-2">{g.source}</td>
                    <td className="px-4 py-2">
                      <StatusBadge status={g.status} />
                    </td>
                    <td className="px-4 py-2">{formatDate(g.starts_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Purchase history</h2>
        {purchases.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No purchases.</p>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Date</th>
                  <th className="px-4 py-2 font-medium">Listing</th>
                  <th className="px-4 py-2 font-medium">Method</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 text-right font-medium">Amount</th>
                </tr>
              </thead>
              <tbody>
                {purchases.map((p) => (
                  <tr key={p.id} className="border-b last:border-0">
                    <td className="px-4 py-2">{formatDate(p.created_at)}</td>
                    <td className="px-4 py-2 font-mono text-xs">{p.listing_id.slice(0, 12)}…</td>
                    <td className="px-4 py-2">{p.payment_method ?? "—"}</td>
                    <td className="px-4 py-2">
                      <StatusBadge status={p.status} />
                    </td>
                    <td className="px-4 py-2 text-right font-mono">
                      {formatMinor(p.amount_minor, p.currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
