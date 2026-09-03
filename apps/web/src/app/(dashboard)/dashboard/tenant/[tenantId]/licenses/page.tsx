"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Pager, QueryError } from "@/components/cp-list";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatDate, formatMinor } from "@/lib/cp";

interface LicenseGrant {
  id: string;
  listing_id: string | null;
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
  // R101[L17]: purchase history ignored pagination meta — older purchases
  // past the backend page size were unreachable.
  const [purchasePage, setPurchasePage] = useState(1);

  const licensesQuery = useQuery({
    queryKey: ["tenant-licenses", tenantId],
    queryFn: () => apiWithAuth<{ data: LicenseGrant[] }>(`/tenants/${tenantId}/licenses`),
  });
  const purchasesQuery = useQuery({
    queryKey: ["tenant-purchases", tenantId, purchasePage],
    queryFn: () =>
      apiWithAuth<{ data: Purchase[]; meta: { has_more: boolean } }>(
        `/tenants/${tenantId}/purchases?page=${purchasePage}&per_page=50`,
      ),
  });

  const licenses = licensesQuery.data?.data ?? [];
  const purchases = purchasesQuery.data?.data ?? [];

  // R113[L0]: learning_path licenses were dead rows — no UI could redeem
  // them (the install endpoint existed but nothing called it).
  const installPath = useMutation({
    mutationFn: (g: LicenseGrant) =>
      apiWithAuth(`/orgs/${g.org_id}/learning-paths/install`, {
        method: "POST",
        body: JSON.stringify({ listing_id: g.listing_id }),
      }),
    onSuccess: () => toast.success("Learning path installed into the organization"),
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Install failed"),
  });

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-3 text-lg font-semibold">Licenses</h2>
        {/* R101[L17]: a failed licenses fetch rendered the "No licenses" empty
            state as if it were authoritative. */}
        {licensesQuery.isError && <QueryError error={licensesQuery.error} what="licenses" />}
        {!licensesQuery.isLoading && !licensesQuery.isError && licenses.length === 0 && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            No licenses. Purchase paid packs from the registry to license them here.
          </p>
        )}
        {licenses.length > 0 && (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Product</th>
                  <th className="px-4 py-2 font-medium">Scope</th>
                  <th className="px-4 py-2 font-medium">Source</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Since</th>
                  <th className="px-4 py-2" />
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
                    <td className="px-4 py-2 text-right">
                      {g.product_type === "learning_path" && g.status === "active" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => installPath.mutate(g)}
                          disabled={installPath.isPending}
                        >
                          Install
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Purchase history</h2>
        {/* R101[L17]: same for purchases — errors masqueraded as "No purchases." */}
        {purchasesQuery.isError && <QueryError error={purchasesQuery.error} what="purchases" />}
        {!purchasesQuery.isLoading && !purchasesQuery.isError && purchases.length === 0 && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No purchases.</p>
        )}
        {purchases.length > 0 && (
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
        <Pager
          page={purchasePage}
          hasMore={purchasesQuery.data?.meta?.has_more ?? false}
          onPage={setPurchasePage}
        />
      </section>
    </div>
  );
}
