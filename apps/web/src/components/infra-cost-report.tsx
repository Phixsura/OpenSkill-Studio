"use client";

interface CostItem { category: string; amount: number; changePct: number; forecast: number; }
interface InfraCostReportProps { items: CostItem[]; displayTotal: string;
  forecastTotal: number; topCategory: string | null; }

export function InfraCostReport({ items, displayTotal, forecastTotal, topCategory }: InfraCostReportProps) {
  const maxAmount = Math.max(...items.map(i => i.amount), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Infrastructure Costs</h3>
        <div className="text-right">
          <div className="text-lg font-bold">{displayTotal}</div>
          <div className="text-[10px] text-gray-400">forecast: ${forecastTotal.toLocaleString()}</div>
        </div>
      </div>
      <div className="p-4 space-y-2">
        {items.map(i => (
          <div key={i.category}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className={i.category === topCategory ? "font-bold" : ""}>{i.category}</span>
              <span className="text-gray-400">${i.amount.toLocaleString()}
                <span className={i.changePct > 0 ? "text-red-500 ml-1" : i.changePct < 0 ? "text-green-600 ml-1" : ""}>
                  {i.changePct > 0 ? "↑" : i.changePct < 0 ? "↓" : ""}{Math.abs(i.changePct)}%
                </span>
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(i.amount / maxAmount) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
