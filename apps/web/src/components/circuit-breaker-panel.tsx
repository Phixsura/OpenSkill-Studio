"use client";

interface Circuit { name: string; state: string; failure_count?: number; }
interface CircuitBreakerPanelProps { circuits: Circuit[]; health: string; }

const STATE_STYLES: Record<string, { color: string; icon: string }> = {
  closed: { color: "text-green-600", icon: "🟢" },
  open: { color: "text-red-600", icon: "🔴" },
  half_open: { color: "text-yellow-600", icon: "🟡" },
};

export function CircuitBreakerPanel({ circuits, health }: CircuitBreakerPanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Circuit Breakers</h3>
        <span className={`text-xs font-medium ${health === "healthy" ? "text-green-600" : health === "degraded" ? "text-yellow-600" : "text-red-600"}`}>
          {health}
        </span>
      </div>
      <ul className="mt-3 space-y-1">
        {circuits.map(c => {
          const style = STATE_STYLES[c.state] || STATE_STYLES.closed;
          return (
            <li key={c.name} className="flex items-center justify-between text-sm">
              <span>{c.name}</span>
              <span className={style.color}>{style.icon} {c.state}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
