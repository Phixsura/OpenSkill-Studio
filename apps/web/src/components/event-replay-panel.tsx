"use client";
interface ReplayEvent { seq: number; type: string; timestamp: number; }
interface EventReplayPanelProps { events: ReplayEvent[]; totalEvents: number; eventTypes: number; }
export function EventReplayPanel({ events, totalEvents, eventTypes }: EventReplayPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏮️ Event Replay</h3>
        <span className="text-xs text-gray-400">{totalEvents} events · {eventTypes} types</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {events.map(e => (
          <div key={e.seq} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-gray-400">#{e.seq}</span>
              <span className="font-mono text-blue-500">{e.type}</span>
            </div>
            <span className="text-gray-400">{e.timestamp}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
