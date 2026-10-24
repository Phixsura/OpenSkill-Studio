"use client";
interface IncCountTrendPanelProps { trend: string; recentAvg: number; olderAvg: number; total: number; }
const TC: Record<string, string> = { worsening: "text-red-500", improving: "text-green-600", stable: "text-gray-400" };
export function IncCountTrendPanel({ trend, recentAvg, olderAvg, total }: IncCountTrendPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Incident Trend</h3>
        <span className={`text-xs font-bold ${TC[trend] ?? ""}`}>{trend} · {total} total</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Recent Avg</span><div className="font-bold text-lg">{recentAvg}/period</div></div>
        <div><span className="text-gray-400">Older Avg</span><div className="font-bold text-lg">{olderAvg}/period</div></div>
      </div>
    </div>
  );
}
