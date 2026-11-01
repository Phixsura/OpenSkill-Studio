"use client";

interface HealthPulseWidgetProps { status: string; emoji: string; scoreDisplay: string;
  checks: Record<string, boolean>; summary: string;
  activeIncidents: number; errorRatePct: number; p99LatencyMs: number; }

export function HealthPulseWidget({ status, emoji, scoreDisplay, checks, summary,
  activeIncidents, errorRatePct, p99LatencyMs }: HealthPulseWidgetProps) {
  return (
    <div className={`rounded-xl border p-5 ${
      status === "healthy" ? "border-green-200 dark:border-green-800" :
      status === "critical" ? "border-red-200 dark:border-red-800" : "border-yellow-200 dark:border-yellow-800"
    }`}>
      <div className="text-center mb-4">
        <p className="text-4xl mb-1">{emoji}</p>
        <p className="text-2xl font-bold">{scoreDisplay}</p>
        <p className="text-sm text-gray-400 capitalize">{status}</p>
      </div>
      <div className="flex justify-center gap-2 mb-3">
        {Object.entries(checks).map(([name, ok]) => (
          <div key={name} className="flex items-center gap-1 text-xs">
            <span className={`w-2 h-2 rounded-full ${ok ? "bg-green-500" : "bg-red-500"}`} />
            <span className="text-gray-400 capitalize">{name}</span>
          </div>
        ))}
      </div>
      <div className="flex justify-center gap-4 text-xs text-gray-400">
        <span>Errors: {errorRatePct}%</span>
        <span>P99: {p99LatencyMs}ms</span>
        {activeIncidents > 0 && <span className="text-red-500">{activeIncidents} incidents</span>}
      </div>
    </div>
  );
}
