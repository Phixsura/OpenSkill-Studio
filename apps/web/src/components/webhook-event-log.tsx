"use client";

interface WebhookEvent { eventId: string; endpointUrl: string; status: string; responseCode: number; attempts: number; createdAt: number; }

const statusColors: Record<string, string> = {
  delivered: "text-green-600", failed: "text-red-600", replayed: "text-blue-600", pending: "text-yellow-600",
};

export function WebhookEventLog({ events, onReplay }: {
  events: WebhookEvent[]; onReplay?: (eventId: string) => void;
}) {
  if (!events.length) return <div className="text-center text-gray-400 py-6 text-sm">No webhook events</div>;
  return (
    <div className="space-y-1">
      {events.map(e => (
        <div key={e.eventId} className="flex items-center justify-between border dark:border-gray-700 rounded-lg p-2.5 text-sm">
          <div className="flex items-center gap-3 min-w-0">
            <span className={`font-medium text-xs ${statusColors[e.status] || ""}`}>{e.status}</span>
            <span className="font-mono text-xs truncate">{e.endpointUrl}</span>
            <span className="text-xs text-gray-400">{e.responseCode > 0 ? e.responseCode : "—"}</span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-xs text-gray-400">{e.attempts}×</span>
            {e.status === "failed" && (
              <button onClick={() => onReplay?.(e.eventId)} className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded">Replay</button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
