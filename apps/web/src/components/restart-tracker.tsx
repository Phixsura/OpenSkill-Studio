"use client";

interface RestartInfo { service: string; restarts: number; ratePerHour: number; crashLoop: boolean; }
interface RestartTrackerProps { services: RestartInfo[]; crashLoopCount: number; allStable: boolean; }

export function RestartTracker({ services, crashLoopCount, allStable }: RestartTrackerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Restart Tracker</h3>
        <span className={`text-xs ${allStable ? "text-green-600" : "text-red-500"}`}>
          {allStable ? "✅ All Stable" : `🔴 ${crashLoopCount} crash-looping`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex justify-between px-4 py-2 text-xs">
            <span className={s.crashLoop ? "text-red-600 font-bold" : ""}>
              {s.crashLoop ? "🔴" : "🟢"} {s.service}
            </span>
            <span className="text-gray-400">{s.restarts} restarts · {s.ratePerHour}/hr</span>
          </div>
        ))}
      </div>
    </div>
  );
}
