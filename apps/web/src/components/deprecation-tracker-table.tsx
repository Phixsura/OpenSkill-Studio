"use client";

interface DeprecatedEndpoint { endpoint: string; sunsetDate: string; replacement: string;
  migrationPct: number; remaining: number; readyToSunset: boolean; }
interface DeprecationTrackerTableProps { items: DeprecatedEndpoint[]; readyToSunset: number; }

export function DeprecationTrackerTable({ items, readyToSunset }: DeprecationTrackerTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚠️ Deprecated Endpoints</h3>
        <span className="text-xs text-gray-400">{readyToSunset} ready to sunset</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {items.map(d => (
          <div key={d.endpoint} className="px-4 py-3">
            <div className="flex justify-between mb-1">
              <code className="text-sm font-mono text-red-500 line-through">{d.endpoint}</code>
              <span className="text-xs text-gray-400">Sunset: {d.sunsetDate}</span>
            </div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-gray-400">→ <code className="text-green-600">{d.replacement}</code></span>
              <span>{d.remaining} callers remaining</span>
            </div>
            <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div className={`h-full rounded-full ${d.readyToSunset ? "bg-green-500" : "bg-blue-500"}`}
                   style={{ width: `${d.migrationPct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
