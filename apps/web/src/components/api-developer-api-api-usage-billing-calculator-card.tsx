"use client";

interface LineItemInfo { description: string; quantity: number; total_cents: number; }
interface InvoiceInfo { invoice_id: string; period: string; line_items: LineItemInfo[]; subtotal_cents: number; discount_cents: number; total_cents: number; }
interface Props { invoice: InvoiceInfo; appName: string; }

function fmtCents(c: number) { return `$${(c / 100).toFixed(2)}`; }

export default function APIDeveloperAPIApiUsageBillingCalculatorCard({ invoice, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💳 Usage Billing</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {invoice.period}</p>
        </div>
        <span className="text-lg font-bold text-green-600">{fmtCents(invoice.total_cents)}</span>
      </div>
      <div className="space-y-1 mb-3">
        {invoice.line_items.map((li, i) => (
          <div key={i} className="flex items-center justify-between text-[11px]">
            <span className="text-gray-700 dark:text-gray-300">{li.description} × {li.quantity.toLocaleString()}</span>
            <span className="text-gray-400">{fmtCents(li.total_cents)}</span>
          </div>
        ))}
      </div>
      <div className="border-t border-gray-100 pt-2 dark:border-gray-800">
        {invoice.discount_cents > 0 && (
          <div className="flex justify-between text-[10px] text-green-600"><span>Discount</span><span>-{fmtCents(invoice.discount_cents)}</span></div>
        )}
        <div className="flex justify-between text-[11px] font-bold text-gray-900 dark:text-gray-100"><span>Total</span><span>{fmtCents(invoice.total_cents)}</span></div>
      </div>
    </div>
  );
}
