"use client";

interface Recording { recording_id: string; user_id: string; page_url: string;
  duration_formatted: string; has_errors: boolean; has_rage_clicks: boolean; event_count: number; }
interface SessionReplayListProps { recordings: Recording[]; frustrationScore: number;
  onPlay: (id: string) => void; }

export function SessionReplayList({ recordings, frustrationScore, onPlay }: SessionReplayListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Session Replays</h2>
        <span className={`text-sm ${frustrationScore > 30 ? "text-red-600" : "text-green-600"}`}>
          Frustration: {frustrationScore}%
        </span>
      </div>
      <div className="space-y-2">
        {recordings.map(r => (
          <button key={r.recording_id} onClick={() => onPlay(r.recording_id)}
            className="flex w-full items-center justify-between rounded-lg border p-3 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
            <div>
              <p className="text-sm font-medium">{r.page_url}</p>
              <p className="text-xs text-gray-400">{r.user_id} · {r.event_count} events · {r.duration_formatted}</p>
            </div>
            <div className="flex items-center gap-1">
              {r.has_errors && <span className="text-xs text-red-500">❌ Error</span>}
              {r.has_rage_clicks && <span className="text-xs text-orange-500">😤 Rage</span>}
              <span className="ml-1 text-xs text-blue-500">▶</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
