"use client";

interface QueuedWebhook {
  webhookId: string;
  url: string;
  priority: "low" | "normal" | "high" | "critical";
  state: "queued" | "delivering" | "delivered" | "failed" | "retry";
  attempt: number;
  maxAttempts: number;
  payloadSize: number;
}

interface QueueDepth {
  total: number;
  pending: number;
  byState: Record<string, number>;
}

const priorityColors: Record<string, string> = {
  low: "bg-gray-100 text-gray-600", normal: "bg-blue-100 text-blue-700",
  high: "bg-orange-100 text-orange-700", critical: "bg-red-100 text-red-700",
};

const stateIcons: Record<string, string> = {
  queued: "⏳", delivering: "🚀", delivered: "✅", failed: "❌", retry: "🔄",
};

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes}B`;
  return `${(bytes / 1024).toFixed(1)}KB`;
}

export function WebhookQueuePanel({
  webhooks,
  depth,
  onFlush,
}: {
  webhooks: QueuedWebhook[];
  depth: QueueDepth;
  onFlush?: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📬 Webhook Queue</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">{depth.pending} pending</span>
          <button onClick={onFlush} className="text-xs bg-red-600 text-white px-2 py-1 rounded">Flush</button>
        </div>
      </div>

      <div className="flex gap-2 text-xs">
        {Object.entries(depth.byState).map(([state, count]) => (
          <span key={state} className="rounded-lg border dark:border-gray-700 px-2 py-1">
            {stateIcons[state] || "●"} {state}: <b>{count}</b>
          </span>
        ))}
      </div>

      <div className="space-y-1">
        {webhooks.map((wh) => (
          <div key={wh.webhookId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
            <div className="flex items-center gap-2 flex-1 min-w-0">
              <span>{stateIcons[wh.state]}</span>
              <span className={`text-xs px-1.5 py-0.5 rounded ${priorityColors[wh.priority]}`}>{wh.priority}</span>
              <code className="text-xs truncate max-w-xs">{wh.url}</code>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400 shrink-0">
              <span>{wh.attempt}/{wh.maxAttempts}</span>
              <span>{formatSize(wh.payloadSize)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
