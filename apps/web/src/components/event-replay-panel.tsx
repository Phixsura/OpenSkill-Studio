"use client";

interface EventReplayPanelProps { replayId: string; eventCount: number; speed: number;
  delivered: number; failed: number; progressPct: number; status: string;
  onPause: () => void; onCancel: () => void; }

export function EventReplayPanel({ replayId, eventCount, speed, delivered, failed,
  progressPct, status, onPause, onCancel }: EventReplayPanelProps) {
  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold">Event Replay</h3>
          <p className="font-mono text-xs text-gray-400">{replayId} · {speed}x speed</p>
        </div>
        <span className={`rounded-full px-2 py-0.5 text-xs ${status === "completed" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-blue-100 text-blue-700 dark:bg-blue-900/30"}`}>
          {status}
        </span>
      </div>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-500 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>{progressPct}%</span>
        <span>✅ {delivered} · ❌ {failed} · ⏳ {eventCount - delivered - failed}</span>
      </div>
      {status !== "completed" && (
        <div className="flex gap-2">
          <button onClick={onPause} className="flex-1 rounded border py-1 text-xs dark:border-gray-600">Pause</button>
          <button onClick={onCancel} className="flex-1 rounded border border-red-300 py-1 text-xs text-red-600">Cancel</button>
        </div>
      )}
    </div>
  );
}
