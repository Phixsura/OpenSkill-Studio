"use client";

interface TimeoutInfo {
  destination: string;
  connect_timeout_ms: number;
  read_timeout_ms: number;
  timeout_count: number;
}

interface APIWebhookTimeoutCardProps {
  configs: TimeoutInfo[];
  appName: string;
}

export default function APIWebhookTimeoutCard({ configs, appName }: APIWebhookTimeoutCardProps) {
  const frequent = configs.filter((c) => c.timeout_count >= 5).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏰ Webhook Timeouts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{configs.length} destinations</span>
          {frequent > 0 && <p className="text-[10px] text-red-500">{frequent} frequent</p>}
        </div>
      </div>

      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No timeout configs</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.destination} className="flex items-center justify-between text-[11px]">
              <span className="truncate max-w-[160px] text-gray-700 dark:text-gray-300">{c.destination}</span>
              <span className="text-gray-400">{c.connect_timeout_ms}ms / {c.read_timeout_ms}ms · {c.timeout_count}x</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
