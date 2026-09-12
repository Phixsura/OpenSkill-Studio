"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Pager, QueryError } from "@/components/cp-list";
import { apiWithAuth } from "@/lib/api";
import { formatDate, formatMinor } from "@/lib/cp";

interface CreditBalance {
  currency: string;
  balance_minor: number;
  reserved_minor: number;
  available_minor: number;
}

interface LedgerEntry {
  id: string;
  entry_type: string;
  amount_minor: number;
  balance_after_minor: number;
  currency: string;
  reference_type: string | null;
  reason: string | null;
  created_at: string;
}

export default function TenantCreditsPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  // R101[M31]: the ledger ignored pagination meta — anything past the backend
  // default page size was silently unreachable.
  const [page, setPage] = useState(1);

  const balancesQuery = useQuery({
    queryKey: ["tenant-credits", tenantId],
    queryFn: () => apiWithAuth<{ data: CreditBalance[] }>(`/tenants/${tenantId}/credits`),
  });
  const ledgerQuery = useQuery({
    queryKey: ["tenant-credit-ledger", tenantId, page],
    queryFn: () =>
      apiWithAuth<{ data: LedgerEntry[]; meta: { has_more: boolean } }>(
        `/tenants/${tenantId}/credits/ledger?page=${page}&per_page=50`,
      ),
  });

  const balances = balancesQuery.data?.data ?? [];
  const ledger = ledgerQuery.data?.data ?? [];

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-3 text-lg font-semibold">Balances</h2>
        {/* R101[M31]: a failed balances fetch rendered the "No credit balance"
            empty state as if it were authoritative. */}
        {balancesQuery.isError && <QueryError error={balancesQuery.error} what="credit balances" />}
        {!balancesQuery.isLoading && !balancesQuery.isError && balances.length === 0 && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            No credit balance yet. Credits are applied to invoices and can prepay usage.
          </p>
        )}
        {balances.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-3">
            {balances.map((b) => (
              <div key={b.currency} className="rounded-lg border p-4">
                <p className="text-xs text-[hsl(var(--muted-foreground))]">{b.currency}</p>
                <p className="mt-1 text-2xl font-bold">
                  {formatMinor(b.available_minor, b.currency)}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">
                  {formatMinor(b.balance_minor, b.currency)} total ·{" "}
                  {formatMinor(b.reserved_minor, b.currency)} reserved
                </p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Ledger</h2>
        {/* R101[M31]: same for the ledger — errors masqueraded as "No entries." */}
        {ledgerQuery.isError && <QueryError error={ledgerQuery.error} what="credit ledger" />}
        {!ledgerQuery.isLoading && !ledgerQuery.isError && ledger.length === 0 && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No entries.</p>
        )}
        {ledger.length > 0 && (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Date</th>
                  <th className="px-4 py-2 font-medium">Type</th>
                  <th className="px-4 py-2 font-medium">Reason</th>
                  <th className="px-4 py-2 text-right font-medium">Amount</th>
                  <th className="px-4 py-2 text-right font-medium">Balance</th>
                </tr>
              </thead>
              <tbody>
                {ledger.map((e) => (
                  <tr key={e.id} className="border-b last:border-0">
                    <td className="px-4 py-2">{formatDate(e.created_at)}</td>
                    <td className="px-4 py-2">
                      <span className="rounded bg-[hsl(var(--secondary))] px-1.5 py-0.5 text-xs">
                        {e.entry_type}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
                      {e.reason ?? e.reference_type ?? "—"}
                    </td>
                    <td
                      className={`px-4 py-2 text-right font-mono ${
                        e.amount_minor < 0 ? "text-red-600" : "text-green-600"
                      }`}
                    >
                      {e.amount_minor >= 0 ? "+" : ""}
                      {formatMinor(e.amount_minor, e.currency)}
                    </td>
                    <td className="px-4 py-2 text-right font-mono">
                      {formatMinor(e.balance_after_minor, e.currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <Pager page={page} hasMore={ledgerQuery.data?.meta?.has_more ?? false} onPage={setPage} />
      </section>
    </div>
  );
}
