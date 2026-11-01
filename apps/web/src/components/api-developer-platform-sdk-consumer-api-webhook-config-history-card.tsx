"use client";

interface Change { id: string; field: string; oldValue: string; newValue: string; changedBy: string; timestamp: string; }
interface Props { webhookId: string; totalChanges: number; mostChangedField: string; changes: Change[]; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiWebhookConfigHistoryCard({ webhookId, totalChanges, mostChangedField, changes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📜 Config History</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {webhookId} · {totalChanges} changes{mostChangedField ? ` · Most changed: ${mostChangedField}` : ""}</p>
      </div>
      {changes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No config changes</p>
      ) : (
        <div className="space-y-2">
          {changes.slice(0, 6).map((c) => (
            <div key={c.id} className="rounded bg-gray-50 px-2 py-1.5 text-[10px] dark:bg-gray-800">
              <div className="flex justify-between">
                <code className="font-medium text-blue-600 dark:text-blue-400">{c.field}</code>
                <span className="text-gray-400">{c.changedBy} · {c.timestamp}</span>
              </div>
              <div className="mt-0.5 text-gray-500"><span className="line-through text-red-400">{c.oldValue}</span> → <span className="text-green-500">{c.newValue}</span></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
