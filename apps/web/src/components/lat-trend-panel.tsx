"use client";
interface LatTrendPanelProps { trend: string; changePct: number; recentP99: number; olderP99: number; }
const TC: Record<string, string> = { worsening: "text-red-500", improving: "text-green-600", stable: "text-gray-400" };
export function LatTrendPanel({ trend, changePct, recentP99, olderP99 }: LatTrendPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Latency Trend</h3>
        <span className={`text-xs font-bold ${TC[trend] ?? ""}`}>{trend} ({changePct > 0 ? "+" : ""}{changePct}%)</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Recent P99</span><div className="font-bold text-lg">{recentP99}ms</div></div>
        <div><span className="text-gray-400">Older P99</span><div className="font-bold text-lg">{olderP99}ms</div></div>
      </div>
    </div>
  );
}
