"use client";
export function FleetAiDepTrackPanel({ trackers, active, deps, outdated, vulns }: { trackers: number; active: number; deps: number; outdated: number; vulns: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI Dependency Tracker</h3>
    <div className="text-sm">{active}/{trackers} active · {deps} deps · {outdated} outdated · {vulns} vulns</div>
  </div>);
}
