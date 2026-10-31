"use client";
export function FleetMttrTrackerV9Panel({ incidents, avgMin }: { incidents: number; avgMin: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 MTTR Tracker v9</h3>
    <div className="text-sm">{incidents} incidents · {avgMin}min avg MTTR</div>
  </div>);
}
