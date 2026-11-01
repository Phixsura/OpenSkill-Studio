"use client";

interface FlagInfo { flag_id: string; name: string; enabled: boolean; rollout_pct: number; allowlist_count: number; }
interface Props { flags: FlagInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiFeatureFlagCard({ flags, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚩 Feature Flags</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {flags.length} flags</p>
      </div>
      {flags.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No feature flags</p>
      ) : (
        <div className="space-y-1.5">
          {flags.map((f) => (
            <div key={f.flag_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${f.enabled ? "bg-green-500" : "bg-gray-300"}`} />
                <span className="text-gray-700 dark:text-gray-300">{f.name}</span>
              </div>
              <span className="text-gray-400">{f.rollout_pct}%{f.allowlist_count > 0 ? ` +${f.allowlist_count}` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
