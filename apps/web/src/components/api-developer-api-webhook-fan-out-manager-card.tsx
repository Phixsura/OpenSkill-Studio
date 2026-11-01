"use client";

interface TargetInfo { target_id: string; destination: string; event_types: string[]; enabled: boolean; delivery_count: number; failure_count: number; }
interface Props { targets: TargetInfo[]; appName: string; }

export default function APIDeveloperAPIWebhookFanOutManagerCard({ targets, appName }: Props) {
  const activeCount = targets.filter(t => t.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Fan-Out Manager</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount}/{targets.length} active</p>
      </div>
      {targets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No fan-out targets</p>
      ) : (
        <div className="space-y-2">
          {targets.map((t) => (
            <div key={t.target_id} className={`rounded-lg px-3 py-2 ${t.enabled ? "bg-gray-50 dark:bg-gray-800" : "bg-gray-100 opacity-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{t.destination}</span>
                <span className="text-gray-400">{t.delivery_count} sent</span>
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {t.event_types.map((e) => (
                  <span key={e} className="rounded bg-blue-50 px-1 py-0.5 text-[9px] text-blue-600 dark:bg-blue-900 dark:text-blue-200">{e}</span>
                ))}
              </div>
              {t.failure_count > 0 && <p className="mt-0.5 text-[10px] text-red-500">{t.failure_count} failures</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
