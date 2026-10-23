"use client";

interface SessionAnalyticsPanelProps { totalSessions: number; avgDurationSec: number;
  avgPages: number; bounceRate: number; bySource: Record<string, number>; }

export function SessionAnalyticsPanel({ totalSessions, avgDurationSec, avgPages, bounceRate, bySource }: SessionAnalyticsPanelProps) {
  const sources = Object.entries(bySource).sort((a, b) => b[1] - a[1]);
  const maxCount = Math.max(...sources.map(([, c]) => c), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Session Analytics</h3>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Sessions", v: totalSessions.toLocaleString() },
          { l: "Avg Duration", v: `${avgDurationSec}s` },
          { l: "Avg Pages", v: String(avgPages) },
          { l: "Bounce Rate", v: `${bounceRate}%` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="p-4 space-y-2">
        <div className="text-xs text-gray-400 mb-1">Traffic Sources</div>
        {sources.map(([src, count]) => (
          <div key={src}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="capitalize">{src}</span><span className="text-gray-400">{count}</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-purple-500 rounded-full" style={{ width: `${(count / maxCount) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
