"use client";
export function FleetSsePanel({ streams, activeConns, eventsPerSec, highVolume }: { streams: number; activeConns: number; eventsPerSec: number; highVolume: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 SSE Streams</h3>
    <div className="text-sm">{activeConns.toLocaleString()} connections · {eventsPerSec.toLocaleString()} eps</div>
    {highVolume && <span className="text-xs text-blue-500">⚡ High volume</span>}
  </div>);
}
