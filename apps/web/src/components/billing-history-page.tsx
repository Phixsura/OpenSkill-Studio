"use client";

interface Invoice { id: string; amountDisplay: string; status: string; date: string; plan: string; }
interface BillingHistoryPageProps { invoices: Invoice[]; totalSpentDisplay: string;
  paid: number; total: number; }

const statusBadge: Record<string, string> = {
  paid: "bg-green-100 text-green-700 dark:bg-green-900/30",
  pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/30",
  refunded: "bg-gray-100 text-gray-500 dark:bg-gray-800",
};

export function BillingHistoryPage({ invoices, totalSpentDisplay, paid, total }: BillingHistoryPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">💳 Billing History</h2>
        <div className="text-right">
          <p className="text-xl font-bold">{totalSpentDisplay}</p>
          <p className="text-xs text-gray-400">{paid}/{total} paid</p>
        </div>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {invoices.map(inv => (
          <div key={inv.id} className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <code className="text-xs text-gray-400">{inv.id}</code>
              <span className="text-sm font-medium">{inv.amountDisplay}</span>
              <span className="text-xs text-gray-400">{inv.plan}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs ${statusBadge[inv.status] ?? ""}`}>{inv.status}</span>
              <time className="text-xs text-gray-400">{inv.date}</time>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
