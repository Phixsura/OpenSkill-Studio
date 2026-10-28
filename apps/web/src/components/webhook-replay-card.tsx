"use client";

interface ReplayInfo {
  replay_id: string;
  original_event_id: string;
  status: "queued" | "replaying" | "succeeded" | "failed";
  attempt: number;
  max_attempts: number;
  error: string;
}

interface WebhookReplayCardProps {
  replays: ReplayInfo[];
  appName: string;
}

const STATUS_STYLES: Record<string, { icon: string; text: string }> = {
  queued: { icon: "⏳", text: "text-gray-500" },
  replaying: { icon: "🔄", text: "text-blue-600 dark:text-blue-400" },
  succeeded: { icon: "✅", text: "text-green-600 dark:text-green-400" },
  failed: { icon: "❌", text: "text-red-600 dark:text-red-400" },
};

export default function WebhookReplayCard({ replays, appName }: WebhookReplayCardProps) {
  const pendingCount = replays.filter(
    (r) => r.status === "queued" || r.status === "replaying",
  ).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Webhook Replay</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {pendingCount > 0 && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
            {pendingCount} pending
          </span>
        )}
      </div>

      {replays.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No replay requests</p>
      ) : (
        <div className="space-y-1.5">
          {replays.map((r) => {
            const st = STATUS_STYLES[r.status] ?? STATUS_STYLES.queued;
            return (
              <div
                key={r.replay_id}
                className="flex items-center justify-between rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <div className="flex items-center gap-2">
                  <span>{st.icon}</span>
                  <div>
                    <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                      {r.original_event_id}
                    </span>
                    {r.error && <p className="text-[10px] text-red-500">{r.error}</p>}
                  </div>
                </div>
                <span className="text-[11px] text-gray-400">
                  {r.attempt}/{r.max_attempts}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
