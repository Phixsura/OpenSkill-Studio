"use client";

interface FlagInfo { flag_id: string; name: string; enabled: boolean; rollout_pct: number; evaluation_count: number; }
interface Props { flags: FlagInfo[]; appName: string; }

export default function APIDeveloperAPIApiFeatureFlagManagerCard({ flags, appName }: Props) {
  const enabledCount = flags.filter(f => f.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚩 Feature Flags</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {enabledCount}/{flags.length} enabled</p>
      </div>
      {flags.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No feature flags</p>
      ) : (
        <div className="space-y-2">
          {flags.map((f) => (
            <div key={f.flag_id} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${f.enabled ? "bg-green-500" : "bg-gray-300"}`} />
                <span className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{f.name}</span>
              </div>
              <div className="text-right">
                <span className="text-[11px] text-blue-600">{f.rollout_pct}%</span>
                <p className="text-[9px] text-gray-400">{f.evaluation_count.toLocaleString()} evals</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
