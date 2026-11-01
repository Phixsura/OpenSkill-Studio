"use client";
interface Peak { hour: number; rps: number; aboveAvgPct: number; }
interface PeakDetectPanelProps { peaks: Peak[]; avgRps: number; maxRps: number; totalHours: number; }
export function PeakDetectPanel({ peaks, avgRps, maxRps, totalHours }: PeakDetectPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Traffic Peaks</h3>
        <span className="text-xs text-gray-400">
          {peaks.length} peaks · avg {avgRps} rps · max {maxRps.toLocaleString()} rps
        </span>
      </div>
      {peaks.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {peaks.map(p => (
            <div key={p.hour} className="flex justify-between px-4 py-1.5 text-xs">
              <span>Hour {p.hour}:00</span>
              <span className="text-red-500 font-bold">{p.rps.toLocaleString()} rps (+{p.aboveAvgPct}%)</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-green-600 text-center">No significant peaks detected</div>
      )}
    </div>
  );
}
