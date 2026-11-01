"use client";

interface InvoiceInfo { invoice_id: string; consumer_id: string; period: string; status: string; total_dollars: string; line_count: number; }
interface Props { invoices: InvoiceInfo[]; outstandingTotal: string; appName: string; }

const statusColor: Record<string, string> = { draft: "text-gray-400", issued: "text-blue-600 dark:text-blue-400", paid: "text-green-600 dark:text-green-400", overdue: "text-red-600 dark:text-red-400", void: "text-gray-400 line-through" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerBillingInvoiceCard({ invoices, outstandingTotal, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💵 Billing</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{outstandingTotal} due</span>
      </div>
      {invoices.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No invoices</p>
      ) : (
        <div className="space-y-1">
          {invoices.map((i) => (
            <div key={i.invoice_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="text-gray-500">{i.period}</span>
                <span className="text-gray-700 dark:text-gray-300">{i.consumer_id}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-medium">{i.total_dollars}</span>
                <span className={statusColor[i.status] ?? "text-gray-400"}>{i.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
