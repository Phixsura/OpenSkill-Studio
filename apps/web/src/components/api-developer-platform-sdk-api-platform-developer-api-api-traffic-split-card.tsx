"use client";

interface TargetInfo { version: string; weight: number; upstream: string; }
interface SplitInfo { split_id: string; endpoint: string; targets: TargetInfo[]; sticky: boolean; }
interface Props { splits: SplitInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiTrafficSplitCard({ splits, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 Traffic Splits</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {splits.length} splits</p>
      </div>
      {splits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No traffic splits</p>
      ) : (
        <div className="space-y-3">
          {splits.map((s) => (
            <div key={s.split_id} className="text-[11px]">
              <div className="mb-1 flex items-center justify-between">
                <span className="font-mono text-gray-700 dark:text-gray-300">{s.endpoint}</span>
                {s.sticky && <span className="text-[9px] text-gray-400">📌 sticky</span>}
              </div>
              <div className="flex gap-1">
                {s.targets.map((t) => (
                  <div key={t.version} className="flex-1 rounded bg-blue-50 p-1 text-center dark:bg-blue-900/20">
                    <div className="font-medium text-blue-700 dark:text-blue-400">{t.version}</div>
                    <div className="text-gray-400">{t.weight}%</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
