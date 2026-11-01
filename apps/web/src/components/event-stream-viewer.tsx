"use client";

interface EventEntry { version: number; type: string; data: Record<string, unknown>; }
interface EventStreamViewerProps { streamId: string; events: EventEntry[]; totalStreams: number; }

export function EventStreamViewer({ streamId, events, totalStreams }: EventStreamViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📜 Event Stream</h3>
        <span className="text-xs text-gray-400">{streamId} · {events.length} events · {totalStreams} streams</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {events.map(e => (
          <div key={e.version} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-gray-400 w-6">v{e.version}</span>
              <span className="font-semibold text-blue-500">{e.type}</span>
            </div>
            <span className="text-gray-400 font-mono truncate max-w-[200px]">{JSON.stringify(e.data)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
