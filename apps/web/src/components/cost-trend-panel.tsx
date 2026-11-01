"use client";
interface CostTrendPanelProps { trend: string; changePct: number; current: number;
  projectedNext: number; totalSpend: number; }
const TREND_COLOR: Record<string, string> = { increasing: "text-red-500", decreasing: "text-green-600", stable: "text-gray-400" };
export function CostTrendPanel({ trend, changePct, current, projectedNext, totalSpend }: CostTrendPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Cost Trend</h3>
        <span className={`text-xs font-bold ${TREND_COLOR[trend] ?? ""}`}>
          {trend} · {changePct > 0 ? "+" : ""}{changePct}%
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Current</span><div className="font-bold text-lg">${current.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Projected</span><div className="font-bold text-lg">${projectedNext.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Total</span><div className="font-bold text-lg">${totalSpend.toLocaleString()}</div></div>
      </div>
    </div>
  );
}
