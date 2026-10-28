"use client";

interface FlagInfo {
  flag_id: string;
  enabled: boolean;
  rollout_pct: number;
  description: string;
  force_enable_count: number;
  force_disable_count: number;
}

interface FeatureFlagCardProps {
  flags: FlagInfo[];
  appName: string;
}

function RolloutBar({ pct }: { pct: number }) {
  if (pct <= 0) return null;
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className="h-1.5 rounded-full bg-blue-500"
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
      <span className="text-[11px] text-gray-500">{pct}%</span>
    </div>
  );
}

function ToggleDot({ enabled }: { enabled: boolean }) {
  return (
    <span
      className={`inline-block h-3 w-3 rounded-full ${
        enabled ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"
      }`}
    />
  );
}

export default function FeatureFlagCard({ flags, appName }: FeatureFlagCardProps) {
  const enabledCount = flags.filter((f) => f.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Feature Flags</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {enabledCount}/{flags.length} enabled
        </span>
      </div>

      {/* Flag list */}
      {flags.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No flags configured</p>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {flags.map((f) => (
            <div
              key={f.flag_id}
              className="flex items-center justify-between py-3 first:pt-0 last:pb-0"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <ToggleDot enabled={f.enabled} />
                  <span className="font-mono text-sm font-medium text-gray-800 dark:text-gray-200">
                    {f.flag_id}
                  </span>
                  {!f.enabled && <span className="text-[10px] text-gray-400">off</span>}
                </div>
                {f.description && (
                  <p className="mt-0.5 pl-5 text-xs text-gray-500 dark:text-gray-400">
                    {f.description}
                  </p>
                )}
                <div className="mt-1 flex items-center gap-3 pl-5">
                  {f.enabled && f.rollout_pct > 0 && f.rollout_pct < 100 && (
                    <RolloutBar pct={f.rollout_pct} />
                  )}
                  {f.enabled && f.rollout_pct >= 100 && (
                    <span className="text-[11px] text-green-600 dark:text-green-400">
                      Full rollout
                    </span>
                  )}
                  {(f.force_enable_count > 0 || f.force_disable_count > 0) && (
                    <span className="text-[11px] text-gray-400">
                      {f.force_enable_count > 0 && `${f.force_enable_count} forced on`}
                      {f.force_enable_count > 0 && f.force_disable_count > 0 && " · "}
                      {f.force_disable_count > 0 && `${f.force_disable_count} forced off`}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
