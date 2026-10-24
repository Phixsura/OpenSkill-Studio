"use client";

interface SseEvent { type: string; id: number; data: Record<string, unknown>; }
interface SseEventStreamProps { channel: string; events: SseEvent[];
  latestId: number; connected: boolean; }

export function SseEventStream({ channel, events, latestId, connected }: SseEventStreamProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">📡 {channel}</h3>
        <div className="flex gap-2 text-xs">
          <span className={connected ? "text-green-600" : "text-red-500"}>
            {connected ? "● Connected" : "○ Disconnected"}
          </span>
          <span className="text-gray-400">#{latestId}</span>
        </div>
      </div>
      <div className="bg-gray-950 text-gray-200 font-mono text-xs max-h-40 overflow-y-auto p-2">
        {events.map(e => (
          <div key={e.id} className="py-0.5">
            <span className="text-gray-500">#{e.id}</span>
            <span className="text-blue-400 ml-1">{e.type}</span>
            <span className="text-gray-400 ml-1">{JSON.stringify(e.data)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
