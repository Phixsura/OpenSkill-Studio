"use client";
export function FleetAiDistLockPanel({ managers, active, locks, acquisitions, contentions }: { managers: number; active: number; locks: number; acquisitions: number; contentions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI Distributed Lock</h3>
    <div className="text-sm">{active}/{managers} active · {locks} locks · {acquisitions.toLocaleString()} acq · {contentions} contentions</div>
  </div>);
}
