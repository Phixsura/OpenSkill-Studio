"use client";

interface RetryConfigInfo {
  config_id: string;
  destination: string;
  strategy: string;
  max_attempts: number;
  initial_delay_ms: number;
}

interface APIWebhookRetryConfigCardProps {
  configs: RetryConfigInfo[];
  appName: string;
}

export default function APIWebhookRetryConfigCard({ configs, appName }: APIWebhookRetryConfigCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Retry Config</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{configs.length} configs</span>
      </div>

      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retry configs</p>
      ) : (
        <div className="space-y-1.5">
          {configs.map((c) => (
            <div key={c.config_id} className="rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <span className="truncate max-w-[180px] text-xs text-gray-700 dark:text-gray-300">{c.destination}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{c.strategy}</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{c.max_attempts} attempts · {c.initial_delay_ms}ms initial</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
