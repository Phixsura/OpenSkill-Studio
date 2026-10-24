"use client";
interface TimeoutInfo { endpoint: string; timeoutMs: number; }
interface TimeoutMgrPanelProps { endpoints: TimeoutInfo[]; defaultMs: number; timeoutsHit: number; }
export function TimeoutMgrPanel({ endpoints, defaultMs, timeoutsHit }: TimeoutMgrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Timeout Manager</h3>
        <span className="text-xs text-gray-400">default: {defaultMs}ms · {timeoutsHit} timeouts</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.endpoint}</span>
            <span className="text-gray-400">{e.timeoutMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
