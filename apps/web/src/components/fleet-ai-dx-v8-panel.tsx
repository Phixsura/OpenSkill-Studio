"use client";
export function FleetAiDxV8Panel({ trackers, active, nps, ttfv, satisfaction }: { trackers: number; active: number; nps: number; ttfv: number; satisfaction: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⭐ AI DX v8</h3>
    <div className="text-sm">{active}/{trackers} active · NPS {nps} · TTFV {ttfv}m · {satisfaction}% satisfaction</div>
  </div>);
}
