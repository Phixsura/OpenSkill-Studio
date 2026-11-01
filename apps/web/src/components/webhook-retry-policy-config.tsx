"use client";

interface RetryStep { attempt: number; delay_sec: number; delay_formatted: string; }
interface WebhookRetryPolicyConfigProps { strategy: string; maxRetries: number;
  schedule: RetryStep[]; totalRetryWindow: string; onSave: (strategy: string, maxRetries: number) => void; }

export function WebhookRetryPolicyConfig({ strategy, maxRetries, schedule, totalRetryWindow, onSave }: WebhookRetryPolicyConfigProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Retry Policy</h2>
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs capitalize dark:bg-gray-800">{strategy}</span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-xl font-bold">{maxRetries}</p>
          <p className="text-xs text-gray-400">Max Retries</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-xl font-bold">{totalRetryWindow}</p>
          <p className="text-xs text-gray-400">Total Window</p>
        </div>
      </div>
      <div className="flex items-center gap-1">
        {schedule.map((s, i) => (
          <div key={s.attempt} className="flex flex-1 flex-col items-center">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700 dark:bg-blue-900/30">
              {s.attempt}
            </div>
            <p className="mt-0.5 text-[10px] text-gray-400">{s.delay_formatted}</p>
            {i < schedule.length - 1 && <span className="text-gray-300">→</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
