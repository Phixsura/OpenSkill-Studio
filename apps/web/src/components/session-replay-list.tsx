"use client";

interface Session { sessionId: string; pageUrl: string; durationDisplay: string; events: number; errors: number; hasErrors: boolean; }
interface SessionReplayListProps { sessions: Session[]; total: number; avgDurationS: number; errorSessions: number; }

export function SessionReplayList({ sessions, total, avgDurationS, errorSessions }: SessionReplayListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Session Replays</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{total} sessions</span>
          <span>avg {Math.floor(avgDurationS / 60)}m</span>
          {errorSessions > 0 && <span className="text-red-600">{errorSessions} with errors</span>}
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {sessions.map(s => (
          <div key={s.sessionId} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2 min-w-0">
              <span className={s.hasErrors ? "text-red-600" : "text-green-600"}>{s.hasErrors ? "⚠" : "▶"}</span>
              <span className="text-xs font-mono truncate max-w-[200px]">{s.pageUrl}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span>{s.events} events</span>
              <span>{s.durationDisplay}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
