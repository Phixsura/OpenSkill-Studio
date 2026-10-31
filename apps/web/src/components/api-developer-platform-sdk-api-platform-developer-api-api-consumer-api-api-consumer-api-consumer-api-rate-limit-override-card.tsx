"use client";

interface Override { id: string; consumerId: string; endpoint: string | null; multiplier: number; reason: string; expiresAt: string; }
interface Props { overrides: Override[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRateLimitOverrideCard({ overrides, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Rate Limit Overrides</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {overrides.length} active</p>
      </div>
      {overrides.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No active overrides</p>
      ) : (
        <div className="space-y-2">
          {overrides.map((o) => (
            <div key={o.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{o.consumerId}</span>
                <span className="font-bold text-blue-600">{o.multiplier}x</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">
                {o.endpoint ?? "All endpoints"} · Expires: {o.expiresAt}
                {o.reason && ` · ${o.reason}`}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
