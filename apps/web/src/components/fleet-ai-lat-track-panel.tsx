"use client";
export function FleetAiLatTrackPanel({ trackers, active, endpoints, p50, p99 }: { trackers: number; active: number; endpoints: number; p50: number; p99: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ AI Latency Tracker</h3>
    <div className="text-sm">{active}/{trackers} active · {endpoints} endpoints · p50 {p50}ms · p99 {p99}ms</div>
  </div>);
}
