"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Pager, QueryError } from "@/components/cp-list";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatDate } from "@/lib/cp";

interface AttributedTenant {
  tenant_id: string;
  name: string;
  slug: string;
  status: string;
  plan_key: string | null;
  created_at: string;
}

export default function PartnerTenantsPage() {
  const { partnerId } = useParams<{ partnerId: string }>();
  // R113[M11]: the backend paginates (page/per_page, default 50) but the page
  // ignored the meta — a big-book partner silently saw only the first 50
  // tenants with no pager.
  const [page, setPage] = useState(1);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["partner-tenants", partnerId, page],
    queryFn: () =>
      apiWithAuth<{ data: AttributedTenant[]; meta: { has_more: boolean } }>(
        `/partners/${partnerId}/tenants?page=${page}&per_page=50`,
      ),
  });
  const tenants = data?.data ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Attributed tenants</h2>
      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
      {/* R101[M29]: partner MEMBERs get 403 here — the old code rendered the
          403 as "No attributed tenants. Provision one…", an authoritative-looking
          empty state that sent non-admins on a wild goose chase. */}
      {isError &&
        (error instanceof ApiError && error.status === 403 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Attributed tenants are visible to partner admins only.
          </p>
        ) : (
          <QueryError error={error} what="attributed tenants" />
        ))}
      {!isLoading && !isError && tenants.length === 0 && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          No attributed tenants. Provision one from the Provision tab.
        </p>
      )}
      {tenants.length > 0 && (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="border-b bg-[hsl(var(--secondary))] text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Slug</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Plan</th>
                <th className="px-4 py-2 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((t) => (
                <tr key={t.tenant_id} className="border-b last:border-0">
                  <td className="px-4 py-2 font-medium">{t.name}</td>
                  <td className="px-4 py-2 font-mono text-xs">{t.slug}</td>
                  <td className="px-4 py-2">
                    <StatusBadge status={t.status} />
                  </td>
                  <td className="px-4 py-2 capitalize">{t.plan_key ?? "—"}</td>
                  <td className="px-4 py-2">{formatDate(t.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Pager page={page} hasMore={data?.meta?.has_more ?? false} onPage={setPage} />
    </div>
  );
}
