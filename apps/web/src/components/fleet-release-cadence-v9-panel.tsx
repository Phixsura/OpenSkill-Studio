"use client";
export function FleetReleaseCadenceV9Panel({ teams, releases }: { teams: number; releases: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚂 Release Cadence v9</h3>
    <div className="text-sm">{teams} teams · {releases} releases/week</div>
  </div>);
}
