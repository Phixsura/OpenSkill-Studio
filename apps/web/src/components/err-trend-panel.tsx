"use client";
interface ErrTrendPanelProps { trend: string; change: number; recentRate: number; olderRate: number; }
const TC: Record<string, string> = { worsening: "text-red-500", improving: "text-green-600", stable: "text-gray-400" };
export function ErrTrendPanel({ trend, change, recentRate, olderRate }: ErrTrendPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📉 Error Trend</h3>
        <span className={`text-xs font-bold ${TC[trend] ?? ""}`}>{trend} ({change > 0 ? "+" : ""}{change}%)</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Recent</span><div className="font-bold text-lg">{recentRate}%</div></div>
        <div><span className="text-gray-400">Older</span><div className="font-bold text-lg">{olderRate}%</div></div>
      </div>
    </div>
  );
}
