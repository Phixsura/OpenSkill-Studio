"use client";
export function FleetAiAdoptionV7Panel({ trackers, active, signups, activated, retained, conversion }: { trackers: number; active: number; signups: number; activated: number; retained: number; conversion: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Adoption v7</h3>
    <div className="text-sm">{active}/{trackers} active · {signups.toLocaleString()} signups · {activated.toLocaleString()} activated · {retained.toLocaleString()} retained · {conversion}%</div>
  </div>);
}
