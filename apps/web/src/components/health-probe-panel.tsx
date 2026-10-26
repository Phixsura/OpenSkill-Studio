"use client";

interface ProbeStatus {
  probeType: "liveness" | "readiness" | "startup";
  healthy: boolean;
  checks: number;
  lastLatencyMs?: number;
  lastMessage?: string;
}

const probeIcons: Record<string, string> = {
  liveness: "💓", readiness: "✅", startup: "🚀",
};

export function HealthProbePanel({
  probes,
  onCheck,
}: {
  probes: ProbeStatus[];
  onCheck?: (probeType: string) => void;
}) {
  const allHealthy = probes.every((p) => p.healthy);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🏥 Health Probes</h2>
        <span className={`text-sm font-bold ${allHealthy ? "text-green-600" : "text-red-600"}`}>
          {allHealthy ? "✅ All Healthy" : "⚠ Degraded"}
        </span>
      </div>

      <div className="grid gap-3">
        {probes.map((probe) => (
          <div key={probe.probeType}
            className={`rounded-xl border-2 p-4 ${probe.healthy ? "border-green-300 dark:border-green-700" : "border-red-300 dark:border-red-700"}`}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xl">{probeIcons[probe.probeType]}</span>
                <span className="font-semibold text-sm capitalize">{probe.probeType}</span>
                <span className={`w-3 h-3 rounded-full ${probe.healthy ? "bg-green-500" : "bg-red-500 animate-pulse"}`} />
              </div>
              <button onClick={() => onCheck?.(probe.probeType)}
                className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Check</button>
            </div>
            <div className="flex gap-3 text-xs text-gray-500">
              <span>{probe.checks} checks</span>
              {probe.lastLatencyMs !== undefined && <span>{probe.lastLatencyMs}ms</span>}
              {probe.lastMessage && <span>{probe.lastMessage}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
