"use client";

interface InvoiceItem { description: string; quantity: number; amountDisplay: string; }
interface InvoiceViewProps { invoiceId: string; orgName: string; plan: string;
  period: string; items: InvoiceItem[]; subtotalDisplay: string;
  taxDisplay: string; totalDisplay: string; status: string; }

export function InvoiceView({ invoiceId, orgName, plan, period, items,
  subtotalDisplay, taxDisplay, totalDisplay, status }: InvoiceViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden max-w-lg">
      <div className="p-5 border-b dark:border-gray-700">
        <div className="flex justify-between">
          <div>
            <h3 className="text-lg font-bold">Invoice</h3>
            <p className="text-xs text-gray-400 font-mono">{invoiceId}</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium">{orgName}</p>
            <p className="text-xs text-gray-400">{plan} · {period}</p>
          </div>
        </div>
      </div>
      <div className="p-5">
        {items.map((item, i) => (
          <div key={i} className="flex justify-between text-sm py-1.5 border-b last:border-0 dark:border-gray-800">
            <span>{item.description} ×{item.quantity}</span>
            <span>{item.amountDisplay}</span>
          </div>
        ))}
        <div className="mt-3 pt-3 border-t dark:border-gray-700 space-y-1 text-sm">
          <div className="flex justify-between"><span>Subtotal</span><span>{subtotalDisplay}</span></div>
          <div className="flex justify-between text-gray-400"><span>Tax</span><span>{taxDisplay}</span></div>
          <div className="flex justify-between font-bold text-lg"><span>Total</span><span>{totalDisplay}</span></div>
        </div>
      </div>
      <div className="px-5 py-3 bg-green-50 dark:bg-green-900/20 text-center text-sm text-green-700 capitalize">{status}</div>
    </div>
  );
}
