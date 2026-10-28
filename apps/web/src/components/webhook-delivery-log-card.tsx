"use client";

interface DeliveryAttemptInfo {
  attempt_id: string;
  event_type: string;
  url: string;
  status_code: number | null;
  success: boolean;
  response_time_ms: number;
  attempt_number: number;
  error: string;
  timestamp: string;
}

interface WebhookDeliveryLogCardProps {
  attempts: DeliveryAttemptInfo[];
  successRate: number;
  avgResponseMs: number;
  appName: string;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  return `${Math.floor(diff / 3_600_000)}h ago`;
}

export default function WebhookDeliveryLogCard({
  attempts,
  successRate,
  avgResponseMs,
  appName,
}: WebhookDeliveryLogCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Webhook Deliveries
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span
            className={
              successRate >= 95
                ? "text-green-600 dark:text-green-400"
                : "text-red-600 dark:text-red-400"
            }
          >
            {successRate.toFixed(1)}% success
          </span>
          <span className="text-gray-400">avg {avgResponseMs.toFixed(0)}ms</span>
        </div>
      </div>

      {attempts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deliveries</p>
      ) : (
        <div className="space-y-1.5">
          {attempts.map((a) => (
            <div
              key={a.attempt_id}
              className="flex items-center justify-between rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2 w-2 rounded-full ${a.success ? "bg-green-500" : "bg-red-500"}`}
                />
                <div>
                  <span className="text-xs text-gray-800 dark:text-gray-200">{a.event_type}</span>
                  <p className="max-w-[200px] truncate font-mono text-[10px] text-gray-400">
                    {a.url}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-gray-400">
                {a.status_code && <span>{a.status_code}</span>}
                {a.attempt_number > 1 && <span>retry #{a.attempt_number}</span>}
                <span>{a.response_time_ms.toFixed(0)}ms</span>
                <span>{timeAgo(a.timestamp)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
