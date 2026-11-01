"use client";
export function FleetAiEdgeInfPanel({ edges, active, locations, requests, p50 }: { edges: number; active: number; locations: number; requests: number; p50: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 AI Edge Inference</h3>
    <div className="text-sm">{active}/{edges} active · {locations} locations · {requests.toLocaleString()} req · p50 {p50}ms</div>
  </div>);
}
