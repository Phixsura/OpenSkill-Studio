"use client";

interface Schedule { attempt: number; delaySec: number; }
interface Props { webhookId: string; strategyType: string; maxRetries: number; baseDelay: number; maxDelay: number; multiplier: number; schedule: Schedule[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookRetryStrategyCard({ webhookId, strategyType, maxRetries, baseDelay, maxDelay, multiplier, schedule, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔁 Retry Strategy</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {webhookId}</p>
      </div>
      <div className="mb-3 space-y-1 text-[11px]">
        <div className="flex justify-between"><span className="text-gray-500">Type:</span><span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{strategyType}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Max retries:</span><span className="text-gray-700 dark:text-gray-300">{maxRetries}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Base delay:</span><span className="text-gray-700 dark:text-gray-300">{baseDelay}s</span></div>
        {strategyType === "exponential" && <div className="flex justify-between"><span className="text-gray-500">Multiplier:</span><span className="text-gray-700 dark:text-gray-300">{multiplier}x</span></div>}
        <div className="flex justify-between"><span className="text-gray-500">Max delay:</span><span className="text-gray-700 dark:text-gray-300">{maxDelay}s</span></div>
      </div>
      {schedule.length > 0 && (
        <div>
          <div className="mb-1 text-[10px] text-gray-400">Schedule preview:</div>
          <div className="flex gap-1">{schedule.map((s) => (
            <span key={s.attempt} className="rounded bg-gray-100 px-1.5 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">#{s.attempt}: {s.delaySec}s</span>
          ))}</div>
        </div>
      )}
    </div>
  );
}
