"use client";

interface WebhookLogInfo {
  log_id: string;
  event_type: string;
  destination: string;
  status_code: number;
  success: boolean;
  duration_ms: number;
}

interface WebhookLogCardProps {
  entries: WebhookLogInfo[];
  successRate: number;
  totalCount: number;
  appName: string;
}

export default function WebhookLogCard({
  entries,
  successRate,
  totalCount,
  appName,
}: WebhookLogCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Webhook Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{totalCount} deliveries</span>
          <p className="text-[10px] text-gray-500">{successRate}% success</p>
        </div>
      </div>

      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No webhook deliveries</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div
              key={e.log_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${e.success ? "bg-green-500" : "bg-red-500"}`}
                />
                <span className="text-xs text-gray-700 dark:text-gray-300">{e.event_type}</span>
                <span
                  className={`text-[10px] ${e.status_code < 400 ? "text-green-600" : "text-red-500"}`}
                >
                  {e.status_code}
                </span>
              </div>
              <span className="text-[10px] text-gray-400">{e.duration_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
