"use client";

interface QueueInfo { name: string; depth: number; enqueueRate: number;
  dequeueRate: number; consumers: number; growing: boolean; health: string; }
interface MqMonitorDashboardProps { queues: QueueInfo[]; totalDepth: number;
  overallHealth: string; alertCount: number; }

const HEALTH_STYLE: Record<string, string> = {
  healthy: "bg-green-100 text-green-700", warning: "bg-yellow-100 text-yellow-700",
  critical: "bg-red-100 text-red-700",
};

export function MqMonitorDashboard({ queues, totalDepth, overallHealth, alertCount }: MqMonitorDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📬 Message Queues</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{totalDepth.toLocaleString()} total msgs</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${HEALTH_STYLE[overallHealth] || ""}`}>{overallHealth}</span>
        </div>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Queue</th><th className="p-3">Depth</th>
          <th className="p-3">In/Out</th><th className="p-3">Consumers</th><th className="p-3">Health</th>
        </tr></thead>
        <tbody>
          {queues.map(q => (
            <tr key={q.name} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 font-medium">{q.name}</td>
              <td className="p-3 text-center font-mono text-xs">{q.depth.toLocaleString()}</td>
              <td className="p-3 text-center text-xs">
                <span className="text-green-600">{q.enqueueRate}</span> / <span className="text-blue-600">{q.dequeueRate}</span>
                {q.growing && <span className="text-red-500 ml-1">↑</span>}
              </td>
              <td className="p-3 text-center">{q.consumers}</td>
              <td className="p-3 text-center">
                <span className={`text-xs px-1.5 py-0.5 rounded ${HEALTH_STYLE[q.health] || ""}`}>{q.health}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
