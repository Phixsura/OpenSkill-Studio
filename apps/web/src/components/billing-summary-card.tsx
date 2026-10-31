"use client";

interface BillingItem { item: string; qty: number; rate: number; cost: number; }

interface BillingSummaryCardProps { items: BillingItem[]; totalUsd: number; tier: string; }

export function BillingSummaryCard({ items, totalUsd, tier }: BillingSummaryCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold">💳 Billing Summary</h4>
        <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs capitalize dark:bg-gray-800">{tier}</span>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="border-b text-xs text-gray-500"><th className="py-1 text-left">Item</th><th className="text-right">Qty</th><th className="text-right">Cost</th></tr></thead>
        <tbody>{items.map(i => (
          <tr key={i.item} className="border-b dark:border-gray-800">
            <td className="py-1">{i.item}</td><td className="text-right">{i.qty.toLocaleString()}</td>
            <td className="text-right">${i.cost.toFixed(4)}</td>
          </tr>
        ))}</tbody>
      </table>
      <p className="mt-2 text-right text-lg font-bold">${totalUsd.toFixed(2)}</p>
    </div>
  );
}
