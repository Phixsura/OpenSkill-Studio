"use client";
export function FleetAiDevExpPanel({ trackers, active, nps, ttfc, docs }: { trackers: number; active: number; nps: number; ttfc: number; docs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⭐ AI Developer Experience</h3>
    <div className="text-sm">{active}/{trackers} active · NPS {nps} · TTFC {ttfc}m · docs {docs}% helpful</div>
  </div>);
}
