"use client";

interface InvoiceInfo {
  invoice_id: string;
  status: "draft" | "sent" | "paid" | "overdue" | "void";
  total_dollars: number;
  due_date: string;
  item_count: number;
}

interface OrgBillingCardProps {
  invoices: InvoiceInfo[];
  outstandingDollars: number;
  appName: string;
}

const STATUS_STYLES: Record<string, { text: string; bg: string }> = {
  draft: { text: "text-gray-500", bg: "bg-gray-100 dark:bg-gray-800" },
  sent: { text: "text-blue-700 dark:text-blue-400", bg: "bg-blue-100 dark:bg-blue-900/30" },
  paid: { text: "text-green-700 dark:text-green-400", bg: "bg-green-100 dark:bg-green-900/30" },
  overdue: { text: "text-red-700 dark:text-red-400", bg: "bg-red-100 dark:bg-red-900/30" },
  void: { text: "text-gray-400", bg: "bg-gray-100 dark:bg-gray-800" },
};

export default function OrgBillingCard({
  invoices,
  outstandingDollars,
  appName,
}: OrgBillingCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Billing</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <p
            className={`text-sm font-bold ${outstandingDollars > 0 ? "text-red-600 dark:text-red-400" : "text-green-600 dark:text-green-400"}`}
          >
            ${outstandingDollars.toFixed(2)}
          </p>
          <p className="text-[10px] text-gray-400">outstanding</p>
        </div>
      </div>

      {invoices.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No invoices</p>
      ) : (
        <div className="space-y-1.5">
          {invoices.map((inv) => {
            const st = STATUS_STYLES[inv.status] ?? STATUS_STYLES.draft;
            return (
              <div
                key={inv.invoice_id}
                className="flex items-center justify-between rounded px-2.5 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium capitalize ${st.bg} ${st.text}`}
                  >
                    {inv.status}
                  </span>
                  <span className="font-mono text-xs text-gray-600 dark:text-gray-400">
                    {inv.invoice_id}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-gray-500">{inv.item_count} items</span>
                  <span className="font-medium text-gray-800 dark:text-gray-200">
                    ${inv.total_dollars.toFixed(2)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
