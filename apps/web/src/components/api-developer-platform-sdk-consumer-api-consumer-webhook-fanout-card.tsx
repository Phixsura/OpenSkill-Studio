"use client";

interface Target { id: string; url: string; active: boolean; filterEvents: string[]; }
interface Props { targets: Target[]; maxTargets: number; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiConsumerWebhookFanoutCard({ targets, maxTargets, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Webhook Fanout</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {targets.length}/{maxTargets} targets</p>
      </div>
      {targets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No fanout targets</p>
      ) : (
        <div className="space-y-2">
          {targets.map((t) => (
            <div key={t.id} className={`rounded-lg bg-gray-50 p-2 dark:bg-gray-800 ${!t.active ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="truncate text-gray-700 dark:text-gray-300">{new URL(t.url).hostname}</span>
                <span className={t.active ? "text-green-500" : "text-gray-400"}>{t.active ? "ON" : "OFF"}</span>
              </div>
              {t.filterEvents.length > 0 && (
                <div className="mt-0.5 flex flex-wrap gap-1">{t.filterEvents.map((e) => <span key={e} className="rounded bg-blue-100 px-1 py-0.5 text-[8px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{e}</span>)}</div>
              )}
              {t.filterEvents.length === 0 && <div className="mt-0.5 text-[9px] text-gray-400">All events</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
