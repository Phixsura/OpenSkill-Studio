"use client";

interface DashInfo { total_replayed: number; successful_replays: number; failed_replays: number; pending_replay: number; replay_success_rate: number; avg_replay_latency_ms: number; }
interface Props { dashboard: DashInfo; appName: string; }

export default function APIDeveloperAPIWebhookReplayDashboardCard({ dashboard: d, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔁 Replay Dashboard</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${d.replay_success_rate >= 95 ? "text-green-600" : "text-yellow-600"}`}>{d.replay_success_rate}%</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          { l: "Replayed", v: d.total_replayed },
          { l: "Success", v: d.successful_replays },
          { l: "Failed", v: d.failed_replays },
          { l: "Pending", v: d.pending_replay },
          { l: "Avg Latency", v: `${d.avg_replay_latency_ms}ms` },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[8px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
