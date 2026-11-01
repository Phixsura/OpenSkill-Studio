"use client";

interface InvoiceLineItem {
  description: string;
  quantity: number;
  unitPrice: number;
  total: number;
}

interface Invoice {
  invoiceId: string;
  period: string;
  status: "paid" | "pending" | "overdue" | "draft";
  issuedAt: string;
  dueAt: string;
  lineItems: InvoiceLineItem[];
  subtotal: number;
  tax: number;
  total: number;
  currency: string;
}

export function BillingInvoiceViewer({
  invoice,
  onPay,
  onDownload,
}: {
  invoice: Invoice;
  onPay?: () => void;
  onDownload?: () => void;
}) {
  const statusConfig: Record<string, { color: string; label: string }> = {
    paid: { color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300", label: "Paid" },
    pending: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300", label: "Pending" },
    overdue: { color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300", label: "Overdue" },
    draft: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300", label: "Draft" },
  };

  const fmt = (cents: number) => `$${(cents / 100).toFixed(2)}`;
  const cfg = statusConfig[invoice.status];

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden max-w-lg">
      {/* Header */}
      <div className="bg-gray-50 dark:bg-gray-800 p-5 flex justify-between items-start">
        <div>
          <h2 className="text-lg font-bold">Invoice #{invoice.invoiceId}</h2>
          <p className="text-sm text-gray-500">{invoice.period}</p>
        </div>
        <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${cfg.color}`}>{cfg.label}</span>
      </div>

      {/* Dates */}
      <div className="px-5 py-3 flex justify-between text-xs text-gray-500 border-b dark:border-gray-700">
        <span>Issued: {invoice.issuedAt}</span>
        <span>Due: {invoice.dueAt}</span>
      </div>

      {/* Line items */}
      <div className="px-5 py-3">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-500 border-b dark:border-gray-700">
              <th className="pb-2">Description</th>
              <th className="pb-2 text-right">Qty</th>
              <th className="pb-2 text-right">Unit Price</th>
              <th className="pb-2 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {invoice.lineItems.map((item, i) => (
              <tr key={i} className="border-b dark:border-gray-800">
                <td className="py-2">{item.description}</td>
                <td className="py-2 text-right">{item.quantity}</td>
                <td className="py-2 text-right font-mono">{fmt(item.unitPrice)}</td>
                <td className="py-2 text-right font-mono">{fmt(item.total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Totals */}
      <div className="px-5 py-3 border-t dark:border-gray-700 space-y-1">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Subtotal</span>
          <span className="font-mono">{fmt(invoice.subtotal)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Tax</span>
          <span className="font-mono">{fmt(invoice.tax)}</span>
        </div>
        <div className="flex justify-between text-base font-bold pt-1 border-t dark:border-gray-700">
          <span>Total ({invoice.currency})</span>
          <span>{fmt(invoice.total)}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="px-5 py-4 flex gap-2 border-t dark:border-gray-700">
        {invoice.status !== "paid" && onPay && (
          <button onClick={onPay} className="flex-1 rounded-lg bg-green-600 text-white py-2 text-sm font-medium">
            💳 Pay Now
          </button>
        )}
        {onDownload && (
          <button onClick={onDownload} className="flex-1 rounded-lg border dark:border-gray-600 py-2 text-sm font-medium">
            📄 Download PDF
          </button>
        )}
      </div>
    </div>
  );
}
