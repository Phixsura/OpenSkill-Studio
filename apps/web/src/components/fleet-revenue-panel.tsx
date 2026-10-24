"use client";
export function FleetRevenuePanel({ mrr, arr, mrrGrowth, ltvCacRatio, unitHealthy }: { mrr: number; arr: number; mrrGrowth: number; ltvCacRatio: number; unitHealthy: boolean; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6">
    <h3 className="font-semibold mb-2 text-center">💰 Revenue</h3>
    <div className="grid grid-cols-2 gap-3 text-center text-sm">
      <div><div className="font-bold">${mrr.toLocaleString()}</div><div className="text-xs text-gray-400">MRR</div></div>
      <div><div className="font-bold">${arr.toLocaleString()}</div><div className="text-xs text-gray-400">ARR</div></div>
      <div><div className="font-bold text-green-600">+{mrrGrowth}%</div><div className="text-xs text-gray-400">Growth</div></div>
      <div><div className={`font-bold ${unitHealthy ? "text-green-600" : "text-red-500"}`}>{ltvCacRatio}x</div><div className="text-xs text-gray-400">LTV/CAC</div></div>
    </div>
  </div>);
}
