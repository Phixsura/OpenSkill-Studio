"use client";

interface RetryStep { attempt: number; delay_s: number; cumulative_s: number; }
interface RetryPolicyViewProps { schedule: RetryStep[]; maxAttempts: number; totalWaitS: number; }

export function RetryPolicyView({ schedule, maxAttempts, totalWaitS }: RetryPolicyViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Retry Policy</h3>
        <span className="text-xs text-gray-400">{maxAttempts} attempts · {totalWaitS}s total</span>
      </div>
      <div className="flex items-end gap-1">
        {schedule.map(s => {
          const maxH = 64;
          const h = Math.max(8, (s.delay_s / (schedule[schedule.length - 1]?.delay_s || 1)) * maxH);
          return (
            <div key={s.attempt} className="flex flex-col items-center gap-1">
              <div className="rounded bg-blue-500 transition-all" style={{ width: 24, height: h }} title={`${s.delay_s}s`} />
              <span className="text-xs text-gray-400">#{s.attempt}</span>
            </div>
          );
        })}
      </div>
      <div className="divide-y rounded-lg border text-xs dark:divide-gray-700 dark:border-gray-700">
        {schedule.map(s => (
          <div key={s.attempt} className="flex justify-between px-3 py-1.5">
            <span>Attempt {s.attempt}</span>
            <span className="text-gray-400">{s.delay_s}s delay · {s.cumulative_s}s total</span>
          </div>
        ))}
      </div>
    </div>
  );
}
