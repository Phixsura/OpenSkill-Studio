"use client";

interface QueueStats { name: string; pending: number; processing: number;
  completed: number; failed: number; health: string; avgLatencyMs: number; }
interface QueueMonitorPanelProps { queues: QueueStats[]; allHealthy: boolean; }

const HEALTH_ICON: Record<string, string> = { healthy: "🟢", degraded: "🟡", critical: "🔴" };

export function QueueMonitorPanel({ queues, allHealthy }: QueueMonitorPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📬 Queue Monitor</h3>
        <span className={`text-xs ${allHealthy ? "text-green-600" : "text-red-500"}`}>
          {allHealthy ? "✅ All Healthy" : "⚠ Issues Detected"}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {queues.map(q => (
          <div key={q.name} className="px-4 py-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">{HEALTH_ICON[q.health]} {q.name}</span>
              <span className="text-xs text-gray-400">{q.avgLatencyMs}ms avg</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>⏳ {q.pending} pending</span>
              <span>⚙️ {q.processing} processing</span>
              <span>✅ {q.completed} done</span>
              {q.failed > 0 && <span className="text-red-500">❌ {q.failed} failed</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
