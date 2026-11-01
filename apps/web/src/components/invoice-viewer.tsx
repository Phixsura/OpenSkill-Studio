"use client";

interface LineItem { description: string; quantity: number; unitPrice: number; total: number; }
interface InvoiceViewerProps { invoiceId: string; customer: string; lineItems: LineItem[];
  subtotal: number; tax: number; total: number; displayTotal: string; }

export function InvoiceViewer({ invoiceId, customer, lineItems, subtotal, tax, total, displayTotal }: InvoiceViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">🧾 Invoice {invoiceId}</h3>
          <div className="text-xs text-gray-400">{customer}</div>
        </div>
        <div className="text-xl font-bold">{displayTotal}</div>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Description</th>
          <th className="p-3 text-right">Qty</th>
          <th className="p-3 text-right">Price</th>
          <th className="p-3 text-right">Total</th>
        </tr></thead>
        <tbody>
          {lineItems.map((li, i) => (
            <tr key={i} className="border-b dark:border-gray-700">
              <td className="p-3">{li.description}</td>
              <td className="p-3 text-right">{li.quantity}</td>
              <td className="p-3 text-right">${li.unitPrice.toFixed(2)}</td>
              <td className="p-3 text-right">${li.total.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot className="text-xs">
          <tr className="border-b dark:border-gray-700">
            <td colSpan={3} className="p-3 text-right text-gray-400">Subtotal</td>
            <td className="p-3 text-right">${subtotal.toFixed(2)}</td>
          </tr>
          <tr className="border-b dark:border-gray-700">
            <td colSpan={3} className="p-3 text-right text-gray-400">Tax</td>
            <td className="p-3 text-right">${tax.toFixed(2)}</td>
          </tr>
          <tr>
            <td colSpan={3} className="p-3 text-right font-bold">Total</td>
            <td className="p-3 text-right font-bold">${total.toFixed(2)}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
