"use client";

interface StreamEvent { seq: number; type: string; stream: string; data: Record<string, unknown>; }
interface EventStreamViewerProps { streamId: string; events: StreamEvent[];
  version: number; totalStreams: number; }

const TYPE_COLOR: Record<string, string> = {
  created: "bg-green-100 text-green-700", paid: "bg-blue-100 text-blue-700",
  shipped: "bg-purple-100 text-purple-700", cancelled: "bg-red-100 text-red-700",
};

export function EventStreamViewer({ streamId, events, version, totalStreams }: EventStreamViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">📜 Event Stream</h3>
          <span className="text-xs text-gray-400">{totalStreams} streams</span>
        </div>
        <p className="text-xs text-gray-400 mt-0.5 font-mono">{streamId} · v{version}</p>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {events.map(e => (
          <div key={e.seq} className="flex items-start gap-3 px-4 py-3">
            <span className="text-xs font-mono text-gray-400 w-6 pt-0.5">#{e.seq}</span>
            <div>
              <span className={`text-xs px-1.5 py-0.5 rounded ${TYPE_COLOR[e.type] || "bg-gray-100 text-gray-600"}`}>{e.type}</span>
              <pre className="text-xs text-gray-500 mt-1">{JSON.stringify(e.data)}</pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
