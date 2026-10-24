"use client";
interface DeprecatedEndpoint { endpoint: string; sunsetDate: string; replacement: string;
  migrationPct: number; readyToSunset: boolean; }
interface ApiDeprecPanelProps { endpoints: DeprecatedEndpoint[]; readyCount: number; }
export function ApiDeprecPanel({ endpoints, readyCount }: ApiDeprecPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚠️ API Deprecations</h3>
        <span className="text-xs text-gray-400">{endpoints.length} deprecated · {readyCount} ready to sunset</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono line-through text-gray-500">{e.endpoint}</span>
              <span className={e.readyToSunset ? "text-green-600" : "text-yellow-600"}>{e.migrationPct}% migrated</span>
            </div>
            <div className="text-gray-400">→ {e.replacement || "no replacement"} · sunset: {e.sunsetDate}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
