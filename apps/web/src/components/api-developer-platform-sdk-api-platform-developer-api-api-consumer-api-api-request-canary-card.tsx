"use client";

interface CanaryInfo { canary_id: string; endpoint: string; canary_pct: number; canary_error_rate: number; should_rollback: boolean; canary_requests: number; stable_requests: number; }
interface Props { canaries: CanaryInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCanaryCard({ canaries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🐤 Canary Deployments</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {canaries.length} canaries</p>
      </div>
      {canaries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No canary deployments</p>
      ) : (
        <div className="space-y-1.5">
          {canaries.map((c) => (
            <div key={c.canary_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{c.endpoint}</span>
                <span className={c.should_rollback ? "font-medium text-red-600 dark:text-red-400" : "text-gray-400"}>{c.canary_pct}% canary{c.should_rollback ? " ⚠️ ROLLBACK" : ""}</span>
              </div>
              <div className="flex gap-2 text-[10px] text-gray-400">
                <span>🐤 {c.canary_requests} ({c.canary_error_rate}% err)</span>
                <span>📦 {c.stable_requests} stable</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
