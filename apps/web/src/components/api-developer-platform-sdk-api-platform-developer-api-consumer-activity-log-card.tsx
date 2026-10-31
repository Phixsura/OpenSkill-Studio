"use client";

interface ActivityInfo { entry_id: string; consumer_id: string; action: string; resource: string; status_code: number; }
interface Props { entries: ActivityInfo[]; totalEntries: number; uniqueConsumers: number; appName: string; }

const actionEmoji: Record<string, string> = { api_call: "🌐", key_created: "🔑", key_revoked: "🚫", scope_changed: "🔄", webhook_subscribed: "🔔", webhook_unsubscribed: "🔕", settings_updated: "⚙️" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerActivityLogCard({ entries, totalEntries, uniqueConsumers, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📜 Activity Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right text-[10px] text-gray-400">
          <div>{totalEntries.toLocaleString()} entries</div>
          <div>{uniqueConsumers} consumers</div>
        </div>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No activity</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.entry_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{actionEmoji[e.action] ?? "•"}</span>
                <span className="text-gray-500">{e.consumer_id}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.resource}</span>
              </div>
              {e.status_code > 0 && <span className={e.status_code < 400 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>{e.status_code}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
