"use client";

interface Props { consumerId: string; active: number; idle: number; max: number; utilPct: number; idleTimeoutSec: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiConnectionPoolCard({ consumerId, active, idle, max, utilPct, idleTimeoutSec, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔌 Connection Pool</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · Idle timeout: {idleTimeoutSec}s</p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{active}</div><div className="text-[10px] text-gray-400">Active</div></div>
        <div className="rounded bg-amber-50 p-1.5 dark:bg-amber-900/20"><div className="font-bold text-amber-600">{idle}</div><div className="text-[10px] text-gray-400">Idle</div></div>
        <div className="rounded bg-gray-100 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-600">{max}</div><div className="text-[10px] text-gray-400">Max</div></div>
      </div>
      <div>
        <div className="flex justify-between text-[10px] text-gray-400"><span>Utilization</span><span>{utilPct}%</span></div>
        <div className="mt-0.5 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${utilPct >= 90 ? "bg-red-500" : utilPct >= 70 ? "bg-amber-500" : "bg-blue-500"}`} style={{ width: `${Math.min(utilPct, 100)}%` }} />
        </div>
      </div>
    </div>
  );
}
