"use client";
interface HealthTrendPanelProps { trend: string; avgUptime: number; recentAvg: number;
  worst: number; best: number; onTrack: boolean; slaTarget: number; risk: string; }
const TREND_STYLE: Record<string, string> = { improving: "text-green-600", degrading: "text-red-500", stable: "text-gray-400" };
const RISK_STYLE: Record<string, string> = { low: "text-green-600", medium: "text-yellow-600", high: "text-red-500" };
export function HealthTrendPanel({ trend, avgUptime, recentAvg, worst, best, onTrack, slaTarget, risk }: HealthTrendPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Health Trend</h3>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-bold ${TREND_STYLE[trend] ?? ""}`}>{trend}</span>
          <span className={`text-xs ${RISK_STYLE[risk] ?? ""}`}>{onTrack ? "✅" : "⚠"} SLA {slaTarget}%</span>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">Avg</span><div className="font-bold">{avgUptime}%</div></div>
        <div><span className="text-gray-400">Recent</span><div className="font-bold">{recentAvg}%</div></div>
        <div><span className="text-gray-400">Best</span><div className="font-bold text-green-600">{best}%</div></div>
        <div><span className="text-gray-400">Worst</span><div className="font-bold text-red-500">{worst}%</div></div>
      </div>
    </div>
  );
}
