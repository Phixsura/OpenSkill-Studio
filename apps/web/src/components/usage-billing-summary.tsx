"use client";

interface BillingBreakdown { range: string; calls: number; rate: number; cost: number; }
interface UsageBillingSummaryProps { apiCalls: number; apiCost: number; storageGb: number;
  storageCost: number; basePrice: number; totalDisplay: string; breakdown: BillingBreakdown[]; }

export function UsageBillingSummary({ apiCalls, apiCost, storageGb, storageCost,
  basePrice, totalDisplay, breakdown }: UsageBillingSummaryProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">💳 Usage Billing</h3>
        <p className="text-2xl font-bold">{totalDisplay}</p>
      </div>
      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm"><span>Base plan</span><span>${basePrice.toFixed(2)}</span></div>
        <div className="flex justify-between text-sm"><span>API calls ({apiCalls.toLocaleString()})</span><span>${apiCost.toFixed(2)}</span></div>
        <div className="flex justify-between text-sm"><span>Storage ({storageGb} GB)</span><span>${storageCost.toFixed(2)}</span></div>
        <div className="border-t dark:border-gray-700 pt-2 flex justify-between text-sm font-bold">
          <span>Total</span><span>{totalDisplay}</span>
        </div>
      </div>
      {breakdown.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-gray-400 mb-1">API Tier Breakdown</h4>
          {breakdown.map((b, i) => (
            <div key={i} className="flex justify-between text-xs text-gray-400 py-0.5">
              <span>{b.range}</span>
              <span>{b.calls.toLocaleString()} × ${b.rate} = ${b.cost.toFixed(2)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
