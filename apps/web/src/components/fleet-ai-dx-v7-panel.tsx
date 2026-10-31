"use client";
export function FleetAiDxV7Panel({ trackers, active, nps, ttfc, docs, sdk }: { trackers: number; active: number; nps: number; ttfc: number; docs: number; sdk: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⭐ AI Developer Experience v7</h3>
    <div className="text-sm">{active}/{trackers} active · NPS {nps} · TTFC {ttfc}m · docs {docs}% · SDK {sdk}%</div>
  </div>);
}
