"use client";

interface Invoice { invoice_id: string; period: string; total: number; status: string; }
interface OrgBillingOverviewProps { orgName: string; invoices: Invoice[];
  totalPaid: number; totalDue: number; onViewInvoice: (id: string) => void; onPay: () => void; }

export function OrgBillingOverview({ orgName, invoices, totalPaid, totalDue, onViewInvoice, onPay }: OrgBillingOverviewProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{orgName} — Billing</h2>
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-lg bg-green-50 p-3 text-center dark:bg-green-900/10">
          <p className="text-xl font-bold text-green-600">${totalPaid.toFixed(2)}</p>
          <p className="text-xs text-gray-400">Total Paid</p>
        </div>
        <div className="rounded-lg bg-red-50 p-3 text-center dark:bg-red-900/10">
          <p className="text-xl font-bold text-red-600">${totalDue.toFixed(2)}</p>
          <p className="text-xs text-gray-400">Outstanding</p>
        </div>
      </div>
      {totalDue > 0 && (
        <button onClick={onPay} className="w-full rounded bg-blue-600 py-2 text-sm font-medium text-white">
          Pay ${totalDue.toFixed(2)}
        </button>
      )}
      <div className="space-y-1.5">
        {invoices.map(inv => (
          <button key={inv.invoice_id} onClick={() => onViewInvoice(inv.invoice_id)}
            className="flex w-full items-center justify-between rounded border px-3 py-2 text-left dark:border-gray-700">
            <div>
              <span className="font-mono text-xs text-gray-400">{inv.invoice_id}</span>
              <p className="text-sm">{inv.period}</p>
            </div>
            <div className="text-right">
              <p className="font-bold">${inv.total.toFixed(2)}</p>
              <span className={`text-xs ${inv.status === "paid" ? "text-green-500" : "text-red-500"}`}>{inv.status}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
