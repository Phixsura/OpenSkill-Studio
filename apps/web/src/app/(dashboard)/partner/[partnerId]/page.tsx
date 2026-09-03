"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

interface PartnerDetail {
  id: string;
  name: string;
  slug: string;
  partner_type: string;
  status: string;
  currency: string;
  contact_email: string | null;
  unsettled_accruals_minor: number;
}

interface Entry {
  id: string;
  share_amount_minor: number;
  currency: string;
  period: string;
  status: string;
}

export default function PartnerOverviewPage() {
  const { partnerId } = useParams<{ partnerId: string }>();

  const partnerQuery = useQuery({
    queryKey: ["partner", partnerId],
    queryFn: () => apiWithAuth<{ data: PartnerDetail }>(`/partners/${partnerId}`),
  });
  const entriesQuery = useQuery({
    queryKey: ["partner-entries", partnerId],
    queryFn: () => apiWithAuth<{ data: Entry[] }>(`/partners/${partnerId}/revenue-share-entries`),
  });

  const partner = partnerQuery.data?.data;
  const entries = entriesQuery.data?.data ?? [];
  // R101[H6]: server-side aggregate — the client-side sum covered only the
  // first page of entries and missed 'approved' status (wrong money).
  const accrued = partner?.unsettled_accruals_minor ?? 0;

  if (partnerQuery.isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (!partner) {
    return <p className="text-sm text-red-600">Failed to load partner.</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-3xl font-bold">{partner.name}</h1>
        <StatusBadge status={partner.status} />
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border p-4">
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Partner type</p>
          <p className="mt-1 font-medium">{partner.partner_type}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Settlement currency</p>
          <p className="mt-1 font-medium">{partner.currency}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Unsettled accruals</p>
          <p className="mt-1 text-xl font-bold">{formatMinor(accrued, partner.currency)}</p>
        </div>
      </div>
      <section>
        <h2 className="mb-3 text-lg font-semibold">Recent revenue share entries</h2>
        {entries.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No entries yet.</p>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Period</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 text-right font-medium">Share</th>
                </tr>
              </thead>
              <tbody>
                {entries.slice(0, 20).map((e) => (
                  <tr key={e.id} className="border-b last:border-0">
                    <td className="px-4 py-2">{e.period}</td>
                    <td className="px-4 py-2">
                      <StatusBadge status={e.status} />
                    </td>
                    <td className="px-4 py-2 text-right font-mono">
                      {formatMinor(e.share_amount_minor, e.currency)}
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
