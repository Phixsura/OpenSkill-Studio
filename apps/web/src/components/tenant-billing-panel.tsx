"use client";

interface LineItem { resource: string; quantity: number; rate: number; cost: number; }
interface TenantBillingPanelProps { tenantId: string; total: number; lineItems: LineItem[]; currency: string; }

export function TenantBillingPanel({ tenantId, total, lineItems, currency }: TenantBillingPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💳 Billing: {tenantId}</h3>
        <span className="text-xs font-bold">${total.toLocaleString()} {currency}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {lineItems.map(li => (
          <div key={li.resource} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span>{li.resource}</span>
            <span className="text-gray-400">{li.quantity} × ${li.rate} = <span className="font-bold">${li.cost}</span></span>
          </div>
        ))}
      </div>
    </div>
  );
}
