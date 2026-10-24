"use client";

interface LineItem { resource: string; amount: number; rate: number; cost: number; unit: string; }
interface CostBreakdownCardProps { plan: string; basePrice: number; variableCost: number;
  total: number; lineItems: LineItem[]; display: string; }

export function CostBreakdownCard({ plan, basePrice, variableCost, total, lineItems, display }: CostBreakdownCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Cost Estimate</h3>
        <div className="text-right">
          <div className="text-lg font-bold">{display}</div>
          <div className="text-[10px] text-gray-400 capitalize">{plan} plan</div>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700 text-sm">
        <div className="flex justify-between px-4 py-2 text-gray-500">
          <span>Base price</span><span>${basePrice.toFixed(2)}</span>
        </div>
        {lineItems.map(li => (
          <div key={li.resource} className="flex justify-between px-4 py-2">
            <div>
              <span className="capitalize">{li.resource.replaceAll("_", " ")}</span>
              <span className="text-xs text-gray-400 ml-1">{li.amount} × ${li.rate} {li.unit}</span>
            </div>
            <span>${li.cost.toFixed(2)}</span>
          </div>
        ))}
        <div className="flex justify-between px-4 py-2 font-bold">
          <span>Total</span><span>${total.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}
