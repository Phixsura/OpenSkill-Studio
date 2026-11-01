"use client";

interface TargetInfo { target_id: string; url: string; active: boolean; delivery_count: number; failure_count: number; }
interface Props { consumerId: string; targets: TargetInfo[]; maxTargets: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookFanoutCard({ consumerId, targets, maxTargets, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Webhook Fanout</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className="text-[10px] text-gray-400">{targets.length}/{maxTargets} targets</span>
      </div>
      {targets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No fanout targets</p>
      ) : (
        <div className="space-y-1">
          {targets.map((t) => (
            <div key={t.target_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${t.active ? "bg-green-500" : "bg-gray-300"}`} />
                <span className="text-gray-700 dark:text-gray-300">{new URL(t.url).hostname}</span>
              </div>
              <span className="text-gray-400">{t.delivery_count}✓ {t.failure_count}✗</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
