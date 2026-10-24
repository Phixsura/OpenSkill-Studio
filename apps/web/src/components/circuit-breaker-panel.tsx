"use client";

interface CircuitBreaker { name: string; state: string; failure_count: number;
  failure_threshold: number; recovery_timeout_sec: number; }
interface CircuitBreakerPanelProps { breakers: CircuitBreaker[]; onReset: (name: string) => void; }

const stateStyle: Record<string, { color: string; icon: string }> = {
  closed: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "🟢" },
  open: { color: "bg-red-100 text-red-700 dark:bg-red-900/30", icon: "🔴" },
  half_open: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "🟡" },
};

export function CircuitBreakerPanel({ breakers, onReset }: CircuitBreakerPanelProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Circuit Breakers</h2>
      {breakers.map(cb => {
        const s = stateStyle[cb.state] ?? stateStyle.closed;
        return (
          <div key={cb.name} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{s.icon}</span>
              <div>
                <span className="font-medium">{cb.name}</span>
                <p className="text-xs text-gray-400">
                  Failures: {cb.failure_count}/{cb.failure_threshold} · Timeout: {cb.recovery_timeout_sec}s
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`rounded-full px-2 py-0.5 text-xs ${s.color}`}>{cb.state}</span>
              {cb.state !== "closed" && (
                <button onClick={() => onReset(cb.name)} className="text-xs text-blue-500">Reset</button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
