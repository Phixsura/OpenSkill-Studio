"use client";

interface DeprecatedEndpoint { path: string; method: string; sunsetDate: string;
  replacement: string; recentCalls: number; }
interface DeprecationManagerProps { endpoints: DeprecatedEndpoint[];
  totalCalls: number; actionNeeded: boolean; }

export function DeprecationManager({ endpoints, totalCalls, actionNeeded }: DeprecationManagerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚠️ Deprecated APIs</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{endpoints.length} deprecated</span>
          {actionNeeded && <span className="text-red-500">{totalCalls} calls still active</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={`${e.method}${e.path}`} className="px-4 py-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono">{e.method} {e.path}</span>
              <span className="text-xs text-red-500">sunset: {e.sunsetDate}</span>
            </div>
            <div className="text-[10px] text-gray-400 mt-0.5">
              → {e.replacement || "no replacement"} · {e.recentCalls} recent calls
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
