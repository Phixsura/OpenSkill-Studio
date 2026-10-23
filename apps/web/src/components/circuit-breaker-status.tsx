"use client";

interface CircuitBreakerStatusProps { services: { name: string; state: string; failures: number; threshold: number; }[]; }

const STATE_STYLE: Record<string, string> = {
  closed: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400",
  open: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400",
  half_open: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400",
};

export function CircuitBreakerStatus({ services }: CircuitBreakerStatusProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">⚡ Circuit Breakers</h3>
      <div className="space-y-2">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <p className="text-sm font-medium">{s.name}</p>
              <p className="text-xs text-gray-400">{s.failures}/{s.threshold} failures</p>
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATE_STYLE[s.state] || ""}`}>
              {s.state.replace("_", " ")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
