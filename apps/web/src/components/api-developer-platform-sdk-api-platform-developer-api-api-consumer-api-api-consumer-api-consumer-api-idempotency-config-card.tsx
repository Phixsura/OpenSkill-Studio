"use client";

interface Props { consumerId: string; ttlSeconds: number; maxKeyLength: number; requiredMethods: string[]; enforce: boolean; keyHeader: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIdempotencyConfigCard({ consumerId, ttlSeconds, maxKeyLength, requiredMethods, enforce, keyHeader, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Idempotency Config</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="space-y-2 text-[11px]">
        <div className="flex justify-between"><span className="text-gray-500">Header:</span><code className="text-gray-700 dark:text-gray-300">{keyHeader}</code></div>
        <div className="flex justify-between"><span className="text-gray-500">TTL:</span><span className="text-gray-700 dark:text-gray-300">{Math.round(ttlSeconds / 3600)}h</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Max key length:</span><span className="text-gray-700 dark:text-gray-300">{maxKeyLength}</span></div>
        <div className="flex justify-between">
          <span className="text-gray-500">Enforce:</span>
          <span className={enforce ? "font-bold text-red-600" : "text-gray-400"}>{enforce ? "Required" : "Optional"}</span>
        </div>
        <div>
          <span className="text-gray-500">Required for: </span>
          {requiredMethods.map((m) => <span key={m} className="mr-1 rounded bg-blue-100 px-1 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{m}</span>)}
        </div>
      </div>
    </div>
  );
}
