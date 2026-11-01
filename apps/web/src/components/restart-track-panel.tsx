"use client";
interface RestartInfo { service: string; restarts: number; crashLoop: boolean; lastReason: string; }
interface RestartTrackPanelProps { services: RestartInfo[]; totalRestarts: number; crashLoops: number; }
export function RestartTrackPanel({ services, totalRestarts, crashLoops }: RestartTrackPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Restart Tracker</h3>
        <span className={`text-xs ${crashLoops > 0 ? "text-red-500" : "text-green-600"}`}>
          {totalRestarts} restarts{crashLoops > 0 ? ` · ⚠ ${crashLoops} crash loops` : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              {s.crashLoop && <span className="text-red-500">🔴</span>}
              <span className={`font-mono ${s.crashLoop ? "text-red-600 font-bold" : ""}`}>{s.service}</span>
            </div>
            <span className="text-gray-400">{s.restarts}x · {s.lastReason}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
