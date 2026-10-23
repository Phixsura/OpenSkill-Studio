"use client";

interface RetryStep { attempt: number; delayMs: number; delayDisplay: string; capped: boolean; }
interface RetryPolicyConfigProps { strategy: string; maxAttempts: number;
  schedule: RetryStep[]; totalWaitDisplay: string; }

export function RetryPolicyConfig({ strategy, maxAttempts, schedule, totalWaitDisplay }: RetryPolicyConfigProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔁 Retry Policy</h3>
        <div className="flex gap-2 text-xs text-gray-400">
          <span className="capitalize">{strategy}</span>
          <span>·</span>
          <span>{maxAttempts} max</span>
          <span>·</span>
          <span>{totalWaitDisplay} total</span>
        </div>
      </div>
      <div className="flex gap-1 items-end h-20 mb-2">
        {schedule.map(s => {
          const maxH = Math.max(...schedule.map(x => x.delayMs));
          const h = (s.delayMs / maxH) * 100;
          return (
            <div key={s.attempt} className="flex-1 flex flex-col items-center gap-1">
              <div className={`w-full rounded-t ${s.capped ? "bg-red-400" : "bg-blue-500"}`}
                   style={{ height: `${h}%` }} />
              <span className="text-[10px] text-gray-400">{s.delayDisplay}</span>
            </div>
          );
        })}
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>Attempt 1</span><span>Attempt {maxAttempts}</span>
      </div>
    </div>
  );
}
