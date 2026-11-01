"use client";

interface Period { id: string; base: number; used: number; rolledIn: number; rolledOut: number; }
interface Props { consumerId: string; periods: Period[]; maxRolloverPct: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerQuotaRolloverCard({ consumerId, periods, maxRolloverPct, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">♻️ Quota Rollover</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · Max rollover: {(maxRolloverPct * 100).toFixed(0)}%</p>
      </div>
      {periods.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No periods</p>
      ) : (
        <div className="space-y-2">
          {periods.map((p) => {
            const total = p.base + p.rolledIn;
            const pct = total > 0 ? Math.round((p.used / total) * 100) : 0;
            return (
              <div key={p.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-medium text-gray-700 dark:text-gray-300">{p.id}</span>
                  <span className="text-gray-500">{pct}% used</span>
                </div>
                <div className="mt-1 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div className="h-full rounded-full bg-blue-500" style={{ width: `${Math.min(pct, 100)}%` }} />
                </div>
                <div className="mt-0.5 flex gap-2 text-[10px] text-gray-400">
                  <span>Base: {p.base.toLocaleString()}</span>
                  {p.rolledIn > 0 && <span className="text-green-500">+{p.rolledIn.toLocaleString()} in</span>}
                  {p.rolledOut > 0 && <span className="text-amber-500">-{p.rolledOut.toLocaleString()} out</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
