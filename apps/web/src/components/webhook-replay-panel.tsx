"use client";

interface QueueEntry { id: string; url: string; originalStatus: number;
  replayCount: number; error: string; }
interface WebhookReplayPanelProps { entries: QueueEntry[]; queueSize: number;
  onReplay: (id: string) => void; onReplayAll: () => void; }

export function WebhookReplayPanel({ entries, queueSize, onReplay, onReplayAll }: WebhookReplayPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold">🔄 Webhook Replay Queue</h3>
          <p className="text-xs text-gray-400">{queueSize} failed deliveries</p>
        </div>
        {queueSize > 0 && (
          <button onClick={onReplayAll}
            className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">Replay All</button>
        )}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map(e => (
          <div key={e.id} className="flex items-center justify-between px-4 py-3">
            <div>
              <p className="text-sm font-mono truncate max-w-xs">{e.url}</p>
              <div className="flex gap-2 mt-0.5 text-xs text-gray-400">
                <span className="text-red-500">HTTP {e.originalStatus}</span>
                {e.replayCount > 0 && <span>{e.replayCount} retries</span>}
                {e.error && <span>{e.error}</span>}
              </div>
            </div>
            <button onClick={() => onReplay(e.id)}
              className="text-xs px-2 py-1 border border-blue-200 text-blue-600 rounded hover:bg-blue-50">Retry</button>
          </div>
        ))}
      </div>
    </div>
  );
}
