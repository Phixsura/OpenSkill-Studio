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

  // R113[L0]/R129[H2/H3]: learning_path licenses were dead rows. The install
  // button renders for every active learning_path grant, but tenant-scope
  // grants carry org_id=NULL and manual grants carry listing_id=NULL — so the
  // mutation must (1) pick an admin org the user actually belongs to when the
  // grant has none, and (2) send product_id when there is no listing_id.
  const orgsQuery = useQuery({
    queryKey: ["my-orgs"],
    queryFn: () =>
      apiWithAuth<{
        data: { id: string; name: string; role: string | null; tenant_id: string | null }[];
      }>("/orgs"),
  });
  // R130[32]: restrict the fallback to admin orgs of THIS tenant — /orgs
  // spans every tenant the user belongs to, and targeting a foreign-tenant
  // org 404s the licensed tenant's grant (or installs into the wrong tenant).
  const adminOrgs = (orgsQuery.data?.data ?? []).filter(
    (o) => (o.role === "owner" || o.role === "admin") && o.tenant_id === tenantId,
  );
  const installPath = useMutation({
    mutationFn: (g: LicenseGrant) => {
      const targetOrg = g.org_id ?? adminOrgs[0]?.id;
      if (!targetOrg) {
        throw new ApiError(
          0,
          "NO_ORG",
          "You must be an owner/admin of an organization in this tenant to install",
        );
      }
      const body = g.listing_id ? { listing_id: g.listing_id } : { product_id: g.product_id };
      return apiWithAuth(`/orgs/${targetOrg}/learning-paths/install`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    },
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
        {/* R130[16]: a failed /orgs fetch silently disabled Install with no
            retry affordance — surface it like the sibling queries. */}
        {orgsQuery.isError && <QueryError error={orgsQuery.error} what="your organizations" />}
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
                      {g.product_type === "learning_path" &&
                        g.status === "active" &&
                        // R130[17]: no button for date-expired grants (status
                        // stays 'active'; expiry is read-time) — clicking
                        // could only fail downstream.
                        (g.expires_at == null || new Date(g.expires_at) > new Date()) && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => installPath.mutate(g)}
                            // R130[16]: also gate on the orgs fetch — while
                            // /orgs is loading or failed, adminOrgs=[] would
                            // throw a false "must be an org owner/admin".
                            disabled={
                              installPath.isPending ||
                              (g.org_id == null && (orgsQuery.isLoading || orgsQuery.isError))
                            }
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
