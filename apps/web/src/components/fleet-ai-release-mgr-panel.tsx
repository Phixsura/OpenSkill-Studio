"use client";
export function FleetAiReleaseMgrPanel({ managers, active, releases, rollbacks, leadTime }: { managers: number; active: number; releases: number; rollbacks: number; leadTime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Release Manager</h3>
    <div className="text-sm">{active}/{managers} active · {releases} releases · {rollbacks} rollbacks · {leadTime}m lead time</div>
  </div>);
}
