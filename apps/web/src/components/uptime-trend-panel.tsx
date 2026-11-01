"use client";
interface UptimeTrendPanelProps { trend: string; recent: number; older: number; current: number; }
const TC: Record<string, string> = { improving: "text-green-600", declining: "text-red-500", stable: "text-gray-400" };
export function UptimeTrendPanel({ trend, recent, older, current }: UptimeTrendPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Uptime Trend</h3>
        <span className={`text-xs font-bold ${TC[trend] ?? ""}`}>{trend} · current {current}%</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Recent Avg</span><div className="font-bold text-lg">{recent}%</div></div>
        <div><span className="text-gray-400">Older Avg</span><div className="font-bold text-lg">{older}%</div></div>
      </div>
    </div>
  );
}
