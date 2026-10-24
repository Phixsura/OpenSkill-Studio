"use client";

interface BillingTier { range: string; units: number; rate: number; cost: number; }
interface UsageBillingCardProps { usage: number; totalCost: number; display: string;
  breakdown: BillingTier[]; projectedMonthly?: number; projectedCost?: number; }

export function UsageBillingCard({ usage, totalCost, display, breakdown, projectedMonthly, projectedCost }: UsageBillingCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Usage Billing</h3>
        <div className="text-right">
          <div className="text-lg font-bold">{display}</div>
          <div className="text-[10px] text-gray-400">{usage.toLocaleString()} units</div>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700 text-sm">
        {breakdown.map((t, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2">
            <div>
              <span className="text-xs text-gray-400">{t.range}</span>
              <span className="text-xs ml-2">{t.units.toLocaleString()} units × ${t.rate}</span>
            </div>
            <span className="text-xs font-mono">${t.cost.toFixed(2)}</span>
          </div>
        ))}
        <div className="flex justify-between px-4 py-2 font-bold text-xs">
          <span>Total</span><span>${totalCost.toFixed(2)}</span>
        </div>
      </div>
      {projectedMonthly !== undefined && (
        <div className="p-3 border-t dark:border-gray-700 bg-blue-50 dark:bg-blue-900/10 text-xs text-blue-700 dark:text-blue-400">
          Projected: {projectedMonthly.toLocaleString()} units/mo → ${projectedCost?.toFixed(2)}/mo
        </div>
      )}
    </div>
  );
}
