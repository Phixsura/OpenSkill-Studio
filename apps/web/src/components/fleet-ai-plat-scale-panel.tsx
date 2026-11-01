"use client";
export function FleetAiPlatScalePanel({ trackers, active, maxRps, currentRps, headroom, autoScale }: { trackers: number; active: number; maxRps: number; currentRps: number; headroom: number; autoScale: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 AI Scalability</h3>
    <div className="text-sm">{active}/{trackers} active · {currentRps.toLocaleString()}/{maxRps.toLocaleString()} RPS · {headroom}% headroom · {autoScale ? "✅ auto" : "⚪ manual"}</div>
  </div>);
}
