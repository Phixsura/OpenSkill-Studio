"use client";

interface ReplayEvent { type: string; target: string; timestampMs: number; }
interface SessionReplayPlayerProps { sessionId: string; userId: string;
  startPage: string; durationDisplay: string; totalEvents: number;
  errorCount: number; events: ReplayEvent[]; }

const EVENT_ICON: Record<string, string> = {
  click: "👆", scroll: "📜", input: "⌨️", error: "❌", navigate: "🔗", resize: "📐",
};

export function SessionReplayPlayer({ sessionId, userId, startPage, durationDisplay,
  totalEvents, errorCount, events }: SessionReplayPlayerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">🎬 Session Replay</h3>
          <span className="text-xs text-gray-400">{durationDisplay}</span>
        </div>
        <div className="flex gap-4 mt-2 text-xs text-gray-400">
          <span>Session: <code>{sessionId}</code></span>
          <span>User: {userId}</span>
          <span>Page: {startPage}</span>
        </div>
      </div>
      <div className="flex gap-4 px-4 py-2 text-xs border-b dark:border-gray-700">
        <span>{totalEvents} events</span>
        {errorCount > 0 && <span className="text-red-500">{errorCount} errors</span>}
      </div>
      <div className="max-h-64 overflow-y-auto">
        {events.map((e, i) => (
          <div key={i} className="flex items-center gap-3 px-4 py-2 text-xs border-b last:border-0 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <span className="text-base">{EVENT_ICON[e.type] || "📌"}</span>
            <span className="font-mono text-gray-400 w-16">{(e.timestampMs / 1000).toFixed(1)}s</span>
            <span className={e.type === "error" ? "text-red-600" : ""}>{e.type}</span>
            <span className="text-gray-400 truncate">{e.target}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
