"use client";
export function FleetLeadTimeV9Panel({ changes, avgMin }: { changes: number; avgMin: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ Lead Time v9</h3>
    <div className="text-sm">{changes} changes · {avgMin}min avg</div>
  </div>);
}
