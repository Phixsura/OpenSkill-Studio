"use client";

interface Breaker { name: string; state: string; failures: number; totalTrips: number; }
interface CircuitBreakerStatusProps { breakers: Breaker[]; }

const STATE_STYLE: Record<string, { bg: string; icon: string }> = {
  closed: { bg: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400", icon: "🟢" },
  open: { bg: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400", icon: "🔴" },
  half_open: { bg: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400", icon: "🟡" },
};

export function CircuitBreakerStatus({ breakers }: CircuitBreakerStatusProps) {
  const openCount = breakers.filter(b => b.state === "open").length;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Circuit Breakers</h3>
        {openCount > 0 && <span className="text-xs text-red-500">⚠ {openCount} open</span>}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {breakers.map(b => {
          const s = STATE_STYLE[b.state] ?? STATE_STYLE.closed;
          return (
            <div key={b.name} className="flex items-center justify-between px-4 py-2.5">
              <div className="flex items-center gap-2">
                <span>{s.icon}</span>
                <span className="text-sm font-medium">{b.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">{b.failures} failures · {b.totalTrips} trips</span>
                <span className={`px-2 py-0.5 text-[10px] rounded-full ${s.bg}`}>{b.state.replaceAll("_", " ")}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
