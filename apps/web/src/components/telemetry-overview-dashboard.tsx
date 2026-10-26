"use client";

interface TelemetrySnapshot {
  metrics: { requests: number; errors: number; errorRate: number; avgLatency: number; p99Latency: number };
  resources: { cpu: number; memoryMb: number };
  signals: { traces: number; slowTraces: number; logErrors: number; logWarns: number };
  health: { score: number; alerts: number };
}

export function TelemetryOverviewDashboard({ snapshot, extensionName }: {
  snapshot: TelemetrySnapshot; extensionName: string;
}) {
  const h = snapshot.health;
  const scoreColor = h.score >= 90 ? "text-green-600" : h.score >= 60 ? "text-yellow-600" : "text-red-600";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📡 {extensionName} Telemetry</h2>
        <div className="flex items-center gap-2">
          <span className={`text-2xl font-bold ${scoreColor}`}>{h.score}</span>
          <span className="text-xs text-gray-500">/ 100</span>
          {h.alerts > 0 && <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">{h.alerts} alerts</span>}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Requests</span>
          <span className="font-bold text-lg">{snapshot.metrics.requests.toLocaleString()}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Error Rate</span>
          <span className={`font-bold text-lg ${snapshot.metrics.errorRate > 5 ? "text-red-600" : "text-green-600"}`}>{snapshot.metrics.errorRate}%</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">p99 Latency</span>
          <span className="font-bold text-lg">{snapshot.metrics.p99Latency}ms</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">CPU</span>
          <span className={`font-bold text-lg ${snapshot.resources.cpu > 80 ? "text-red-600" : ""}`}>{snapshot.resources.cpu}%</span>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Memory</span>
          <span className="font-bold">{snapshot.resources.memoryMb}MB</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Traces</span>
          <span className="font-bold">{snapshot.signals.traces}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Log Errors</span>
          <span className="font-bold text-red-500">{snapshot.signals.logErrors}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Log Warns</span>
          <span className="font-bold text-yellow-600">{snapshot.signals.logWarns}</span>
        </div>
      </div>
    </div>
  );
}
