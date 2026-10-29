"use client";

interface ReplayInfo { replay_id: string; event_type: string; destination: string; status: string; }
interface Props { replays: ReplayInfo[]; stats: Record<string, number>; appName: string; }

const sDot: Record<string, string> = { pending: "bg-gray-400", replaying: "bg-blue-500", success: "bg-green-500", failure: "bg-red-500" };

export default function APIDeveloperAPIApiWebhookReplayManagerCard({ replays, stats, appName }: Props) {
  const pendingCount = (stats.pending ?? 0) + (stats.replaying ?? 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Webhook Replays</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {pendingCount > 0 && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] text-blue-700">{pendingCount} pending</span>}
      </div>
      <div className="mb-3 flex gap-3 text-[10px]">
        {Object.entries(stats).filter(([, v]) => v > 0).map(([s, c]) => (
          <span key={s} className="text-gray-400">{s}: {c}</span>
        ))}
      </div>
      {replays.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No replays</p>
      ) : (
        <div className="space-y-1">
          {replays.map((r) => (
            <div key={r.replay_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${sDot[r.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{r.event_type}</span>
              </div>
              <span className="text-gray-400">{r.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
