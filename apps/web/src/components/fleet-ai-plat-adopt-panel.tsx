"use client";
export function FleetAiPlatAdoptPanel({ trackers, active, signups, activated, retained, conversion }: { trackers: number; active: number; signups: number; activated: number; retained: number; conversion: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Platform Adoption</h3>
    <div className="text-sm">{active}/{trackers} active · {signups.toLocaleString()} signups · {activated} activated · {retained} retained · {conversion}% conv</div>
  </div>);
}
