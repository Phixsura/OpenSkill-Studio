"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth } from "@/lib/api";
import { formatDate, formatMinor, type InvoiceLine, type InvoiceSummary } from "@/lib/cp";

// R101[L5]: interface must mirror _invoice_response — the backend never sends
// "period" (rendered undefined dates) and DOES send tax_minor/paid_at, which
// the page silently dropped from the totals.
interface InvoiceDetail extends InvoiceSummary {
  lines: InvoiceLine[];
  payments: {
    id: string;
    amount_minor: number;
    method: string;
    status: string;
    received_at: string | null;
  }[];
  tax_minor: number;
  paid_at: string | null;
}

export default function InvoiceDetailPage() {
  const { tenantId, invoiceId } = useParams<{ tenantId: string; invoiceId: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["tenant-invoice", tenantId, invoiceId],
    queryFn: () =>
      apiWithAuth<{ data: InvoiceDetail }>(`/tenants/${tenantId}/invoices/${invoiceId}`),
  });
  const invoice = data?.data;

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError || !invoice) {
    return <p className="text-sm text-red-600">Failed to load invoice.</p>;
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 print:max-w-none">
      <div className="flex items-center justify-between print:hidden">
        <h1 className="text-2xl font-bold">Invoice {invoice.number ?? ""}</h1>
        <Button variant="outline" onClick={() => window.print()}>
          Print
        </Button>
      </div>

      <div className="rounded-lg border p-6 print:border-0">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-lg font-semibold">{invoice.number ?? invoice.id}</p>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              Issued {formatDate(invoice.issued_at)}
              {invoice.due_at ? ` · Due ${formatDate(invoice.due_at)}` : ""}
            </p>
            {invoice.paid_at && (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                Paid {formatDate(invoice.paid_at)}
              </p>
            )}
          </div>
          <StatusBadge status={invoice.status} />
        </div>

        <table className="w-full text-sm">
          <thead className="border-b text-left">
            <tr>
              <th className="py-2 font-medium">Description</th>
              <th className="py-2 text-right font-medium">Qty</th>
              <th className="py-2 text-right font-medium">Amount</th>
            </tr>
          </thead>
          <tbody>
            {invoice.lines.map((line) => (
              <tr key={line.id} className="border-b last:border-0">
                <td className="py-2">
                  <span className="mr-2 rounded bg-[hsl(var(--secondary))] px-1.5 py-0.5 text-xs">
                    {line.line_type}
                  </span>
                  {line.description}
                </td>
                <td className="py-2 text-right">{line.quantity}</td>
                <td className="py-2 text-right font-mono">
                  {formatMinor(line.amount_minor, invoice.currency)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="ml-auto mt-4 w-64 space-y-1 text-sm">
          <div className="flex justify-between">
            <span className="text-[hsl(var(--muted-foreground))]">Subtotal</span>
            <span className="font-mono">
              {formatMinor(invoice.subtotal_minor, invoice.currency)}
            </span>
          </div>
          {invoice.credit_applied_minor !== 0 && (
            <div className="flex justify-between">
              <span className="text-[hsl(var(--muted-foreground))]">Credit applied</span>
              <span className="font-mono">
                −{formatMinor(Math.abs(invoice.credit_applied_minor), invoice.currency)}
              </span>
            </div>
          )}
          {invoice.tax_minor !== 0 && (
            <div className="flex justify-between">
              <span className="text-[hsl(var(--muted-foreground))]">Tax</span>
              <span className="font-mono">{formatMinor(invoice.tax_minor, invoice.currency)}</span>
            </div>
          )}
          <div className="flex justify-between border-t pt-1 font-semibold">
            <span>Amount due</span>
            <span className="font-mono">
              {formatMinor(invoice.amount_due_minor, invoice.currency)}
            </span>
          </div>
        </div>
      </div>

      {invoice.payments.length > 0 && (
        <div className="print:hidden">
          <h2 className="mb-2 text-lg font-semibold">Payments</h2>
          <div className="rounded-lg border">
            <table className="w-full text-sm">
              <tbody>
                {invoice.payments.map((p) => (
                  <tr key={p.id} className="border-b last:border-0">
                    <td className="px-4 py-2">{p.method}</td>
                    <td className="px-4 py-2">
                      <StatusBadge status={p.status} />
                    </td>
                    <td className="px-4 py-2">{formatDate(p.received_at)}</td>
                    <td className="px-4 py-2 text-right font-mono">
                      {formatMinor(p.amount_minor, invoice.currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
