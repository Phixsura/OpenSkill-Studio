"use client";

interface Replay { replayId: string; webhookId: string; attempts: number;
  maxRetries: number; status: string; }
interface WebhookReplayMgrProps { replays: Replay[]; deliveryRate: number;
  pending: number; exhausted: number; onReplay: (id: string) => void; }

const STATUS_COLORS: Record<string, string> = {
  delivered: "bg-green-100 text-green-700", exhausted: "bg-red-100 text-red-700",
  pending: "bg-gray-200 text-gray-600", retrying: "bg-yellow-100 text-yellow-700",
};

export function WebhookReplayMgr({ replays, deliveryRate, pending, exhausted, onReplay }: WebhookReplayMgrProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔁 Webhook Replay</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{deliveryRate}% delivered</span>
          {pending > 0 && <span className="text-yellow-600">{pending} pending</span>}
          {exhausted > 0 && <span className="text-red-500">{exhausted} failed</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {replays.map(r => (
          <div key={r.replayId} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className="font-mono">{r.webhookId}</span>
              <span className="text-gray-400 ml-2">{r.attempts}/{r.maxRetries}</span>
            </div>
            <div className="flex gap-2">
              <span className={`px-1.5 py-0.5 rounded ${STATUS_COLORS[r.status] ?? ""}`}>{r.status}</span>
              {r.status !== "delivered" && (
                <button onClick={() => onReplay(r.replayId)} className="text-blue-500">↻</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
