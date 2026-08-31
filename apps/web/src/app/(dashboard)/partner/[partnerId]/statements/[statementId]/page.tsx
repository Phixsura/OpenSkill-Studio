"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatDate, formatMinor } from "@/lib/cp";
import { useAuthStore } from "@/stores/auth";

interface Entry {
  id: string;
  source_type: string;
  source_id: string;
  revenue_base_minor: number;
  share_amount_minor: number;
  currency: string;
  status: string;
  created_at: string;
}

interface StatementDetail {
  id: string;
  period: string;
  status: string;
  currency: string;
  opening_adjustments_minor: number;
  gross_revenue_minor: number;
  refunds_minor: number;
  share_total_minor: number;
  manual_adjustments_minor: number;
  net_amount_minor: number;
  finalized_at: string | null;
  external_payment_ref: string | null;
  entries: Entry[];
  entry_count: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export default function StatementDetailPage() {
  const { partnerId, statementId } = useParams<{ partnerId: string; statementId: string }>();

  const { data, isLoading } = useQuery({
    queryKey: ["partner-statement", partnerId, statementId],
    queryFn: () =>
      apiWithAuth<{ data: StatementDetail }>(`/partners/${partnerId}/statements/${statementId}`),
  });
  const stmt = data?.data;

  const downloadCsv = async () => {
    try {
      const token = useAuthStore.getState().accessToken;
      const res = await fetch(
        `${API_BASE}/api/v1/partners/${partnerId}/statements/${statementId}/export.csv`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} },
      );
      if (!res.ok) throw new ApiError(res.status, "EXPORT_FAILED", "Export failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `statement-${stmt?.period ?? statementId}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("CSV export failed");
    }
  };

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (!stmt) {
    return <p className="text-sm text-red-600">Failed to load statement.</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">Statement {stmt.period}</h1>
          <StatusBadge status={stmt.status} />
        </div>
        <Button variant="outline" onClick={downloadCsv}>
          Export CSV
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <Amount label="Gross revenue" value={stmt.gross_revenue_minor} currency={stmt.currency} />
        <Amount label="Refunds" value={stmt.refunds_minor} currency={stmt.currency} />
        <Amount label="Share total" value={stmt.share_total_minor} currency={stmt.currency} />
        <Amount
          label="Opening adj."
          value={stmt.opening_adjustments_minor}
          currency={stmt.currency}
        />
        <Amount
          label="Manual adj."
          value={stmt.manual_adjustments_minor}
          currency={stmt.currency}
        />
        <Amount label="Net" value={stmt.net_amount_minor} currency={stmt.currency} bold />
      </div>

      {stmt.finalized_at && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Finalized {formatDate(stmt.finalized_at)}
          {stmt.external_payment_ref ? ` · Paid ref ${stmt.external_payment_ref}` : ""}
        </p>
      )}

      <section>
        <h2 className="mb-3 text-lg font-semibold">Entries ({stmt.entry_count})</h2>
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="border-b bg-[hsl(var(--secondary))] text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Source</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 text-right font-medium">Base</th>
                <th className="px-4 py-2 text-right font-medium">Share</th>
              </tr>
            </thead>
            <tbody>
              {stmt.entries.map((e) => (
                <tr key={e.id} className="border-b last:border-0">
                  <td className="px-4 py-2">
                    <span className="rounded bg-[hsl(var(--secondary))] px-1.5 py-0.5 text-xs">
                      {e.source_type}
                    </span>{" "}
                    <span className="font-mono text-xs">{e.source_id.slice(0, 12)}…</span>
                  </td>
                  <td className="px-4 py-2">
                    <StatusBadge status={e.status} />
                  </td>
                  <td className="px-4 py-2 text-right font-mono">
                    {formatMinor(e.revenue_base_minor, e.currency)}
                  </td>
                  <td className="px-4 py-2 text-right font-mono">
                    {formatMinor(e.share_amount_minor, e.currency)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function Amount({
  label,
  value,
  currency,
  bold,
}: {
  label: string;
  value: number;
  currency: string;
  bold?: boolean;
}) {
  return (
    <div className="rounded-lg border p-3">
      <p className="text-xs text-[hsl(var(--muted-foreground))]">{label}</p>
      <p className={`mt-1 font-mono text-sm ${bold ? "font-bold" : ""}`}>
        {formatMinor(value, currency)}
      </p>
    </div>
  );
}
