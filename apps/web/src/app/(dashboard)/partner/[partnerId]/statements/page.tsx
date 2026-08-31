"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

interface Statement {
  id: string;
  period: string;
  status: string;
  currency: string;
  share_total_minor: number;
  net_amount_minor: number;
  external_payment_ref: string | null;
}

export default function PartnerStatementsPage() {
  const { partnerId } = useParams<{ partnerId: string }>();

  const { data, isLoading } = useQuery({
    queryKey: ["partner-statements", partnerId],
    queryFn: () => apiWithAuth<{ data: Statement[] }>(`/partners/${partnerId}/statements`),
  });
  const statements = data?.data ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Settlement statements</h2>
      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
      {!isLoading && statements.length === 0 && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">No statements yet.</p>
      )}
      {statements.length > 0 && (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="border-b bg-[hsl(var(--secondary))] text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Period</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 text-right font-medium">Share total</th>
                <th className="px-4 py-2 text-right font-medium">Net</th>
                <th className="px-4 py-2 font-medium">Payment ref</th>
              </tr>
            </thead>
            <tbody>
              {statements.map((s) => (
                <tr key={s.id} className="border-b last:border-0">
                  <td className="px-4 py-2">
                    <Link
                      href={`/partner/${partnerId}/statements/${s.id}`}
                      className="underline-offset-2 hover:underline"
                    >
                      {s.period}
                    </Link>
                  </td>
                  <td className="px-4 py-2">
                    <StatusBadge status={s.status} />
                  </td>
                  <td className="px-4 py-2 text-right font-mono">
                    {formatMinor(s.share_total_minor, s.currency)}
                  </td>
                  <td className="px-4 py-2 text-right font-mono">
                    {formatMinor(s.net_amount_minor, s.currency)}
                  </td>
                  <td className="px-4 py-2 font-mono text-xs">{s.external_payment_ref ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
