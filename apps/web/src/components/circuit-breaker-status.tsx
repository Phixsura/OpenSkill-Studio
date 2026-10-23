"use client";

interface CircuitBreakerStatusProps { state: string; failures: number; threshold: number; recoveryTimeoutS: number; }

const stateConfig: Record<string, { color: string; icon: string }> = {
  closed: { color: "text-green-600", icon: "🟢" },
  open: { color: "text-red-600", icon: "🔴" },
  half_open: { color: "text-yellow-600", icon: "🟡" },
};

export function CircuitBreakerStatus({ state, failures, threshold, recoveryTimeoutS }: CircuitBreakerStatusProps) {
  const cfg = stateConfig[state] ?? stateConfig.closed;
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Circuit Breaker</h3>
        <div className="flex items-center gap-1.5">
          <span>{cfg.icon}</span>
          <span className={`text-sm font-medium capitalize ${cfg.color}`}>{state.replace("_", " ")}</span>
        </div>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-3 text-center">
        <div>
          <p className="text-lg font-bold">{failures}/{threshold}</p>
          <p className="text-xs text-gray-400">Failures</p>
        </div>
        <div>
          <p className="text-lg font-bold">{threshold}</p>
          <p className="text-xs text-gray-400">Threshold</p>
        </div>
        <div>
          <p className="text-lg font-bold">{recoveryTimeoutS}s</p>
          <p className="text-xs text-gray-400">Recovery</p>
        </div>
      </div>
    </div>
  );
}
