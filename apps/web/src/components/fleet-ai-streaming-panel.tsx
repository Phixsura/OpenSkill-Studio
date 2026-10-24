"use client";
export function FleetAiStreamingPanel({ streams, active, connections, tps, ttft }: { streams: number; active: number; connections: number; tps: number; ttft: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌊 AI Streaming</h3>
    <div className="text-sm">{active}/{streams} active · {connections.toLocaleString()} conn · {tps.toLocaleString()} tok/s · TTFT {ttft}ms</div>
  </div>);
}
