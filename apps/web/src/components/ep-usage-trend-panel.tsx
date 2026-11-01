"use client";
interface EpTrend { endpoint: string; changePct: number; recentAvg: number; }
interface EpUsageTrendPanelProps { trends: EpTrend[]; }
export function EpUsageTrendPanel({ trends }: EpUsageTrendPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Usage Trends</h3>
        <span className="text-xs text-gray-400">{trends.length} endpoints trending</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {trends.map(t => (
          <div key={t.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{t.endpoint}</span>
            <span className={t.changePct > 0 ? "text-green-600" : "text-red-500"}>
              {t.changePct > 0 ? "+" : ""}{t.changePct}% · {t.recentAvg.toLocaleString()}/period
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
