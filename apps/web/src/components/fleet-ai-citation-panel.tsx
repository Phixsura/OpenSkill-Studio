"use client";
export function FleetAiCitationPanel({ trackers, active, citations, verified, accuracy }: { trackers: number; active: number; citations: number; verified: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📎 AI Citation Tracker</h3>
    <div className="text-sm">{active}/{trackers} active · {citations.toLocaleString()} citations · {verified.toLocaleString()} verified · {accuracy}% acc</div>
  </div>);
}
