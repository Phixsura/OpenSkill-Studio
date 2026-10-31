"use client";

interface ObservAlert { type: string; source: string; message: string; }
interface ObservHubDashProps { totalMetrics: number; uniqueMetrics: number; totalLogs: number;
  logLevels: Record<string, number>; totalTraces: number; avgTraceMs: number;
  activeAlerts: number; recentAlerts: ObservAlert[]; }

export function ObservHubDash({ totalMetrics, uniqueMetrics, totalLogs, logLevels,
  totalTraces, avgTraceMs, activeAlerts, recentAlerts }: ObservHubDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔭 Observability Hub</h3>
        <span className={`text-xs ${activeAlerts > 0 ? "text-red-500" : "text-green-600"}`}>
          {activeAlerts > 0 ? `🔔 ${activeAlerts} alerts` : "✅ Clear"}
        </span>
      </div>
      <div className="grid grid-cols-4 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Metrics</div><div className="font-bold text-lg">{totalMetrics.toLocaleString()}</div><div className="text-gray-400">{uniqueMetrics} unique</div></div>
        <div><div className="text-gray-400">Logs</div><div className="font-bold text-lg">{totalLogs.toLocaleString()}</div>
          <div className="text-gray-400">{logLevels.error ?? 0} errors</div></div>
        <div><div className="text-gray-400">Traces</div><div className="font-bold text-lg">{totalTraces.toLocaleString()}</div>
          <div className="text-gray-400">{avgTraceMs}ms avg</div></div>
        <div><div className="text-gray-400">Alerts</div><div className={`font-bold text-lg ${activeAlerts > 0 ? "text-red-500" : "text-green-600"}`}>{activeAlerts}</div></div>
      </div>
      {recentAlerts.length > 0 && (
        <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
          {recentAlerts.map((a, i) => (
            <div key={i} className="flex justify-between px-4 py-1.5 text-xs text-red-600">
              <span className="font-mono">{a.source}</span>
              <span className="truncate ml-2 max-w-[200px]">{a.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
