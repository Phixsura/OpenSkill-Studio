"use client";

interface Flag { id: string; name: string; enabled: boolean; hasOverride: boolean; rolloutPct: number; }
interface Props { flags: Flag[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiFeatureFlagCard({ flags, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚩 Feature Flags</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {flags.filter(f => f.enabled).length}/{flags.length} enabled</p>
      </div>
      {flags.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No feature flags</p>
      ) : (
        <div className="space-y-1">
          {flags.map((f) => (
            <div key={f.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <span className="text-gray-700 dark:text-gray-300">{f.name}</span>
                {f.hasOverride && <span className="text-[9px] text-blue-400">override</span>}
                {f.rolloutPct > 0 && f.rolloutPct < 100 && <span className="text-[9px] text-gray-400">{f.rolloutPct}%</span>}
              </div>
              <span className={`font-bold ${f.enabled ? "text-green-500" : "text-gray-400"}`}>{f.enabled ? "ON" : "OFF"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
