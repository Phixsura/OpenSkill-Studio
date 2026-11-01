"use client";

interface LineItem { description: string; quantity: number; totalCents: number; }
interface InvoiceInfo { id: string; period: string; status: string; totalCents: number; lineItems: LineItem[]; }
interface Props { invoices: InvoiceInfo[]; consumerId: string; appName: string; }

const fmtCost = (cents: number) => `$${(cents / 100).toFixed(2)}`;
const statusColors: Record<string, string> = {
  draft: "bg-gray-200 text-gray-600", issued: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  paid: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400", overdue: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  void: "bg-gray-300 text-gray-500 line-through",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerBillingInvoiceCard({ invoices, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧾 Billing Invoices</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {invoices.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No invoices</p>
      ) : (
        <div className="space-y-2">
          {invoices.slice(0, 5).map((inv) => (
            <div key={inv.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{inv.period}</span>
                <div className="flex gap-2">
                  <span className="font-bold">{fmtCost(inv.totalCents)}</span>
                  <span className={`rounded px-1 py-0.5 text-[9px] ${statusColors[inv.status] ?? ""}`}>{inv.status}</span>
                </div>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">{inv.lineItems.length} items</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
