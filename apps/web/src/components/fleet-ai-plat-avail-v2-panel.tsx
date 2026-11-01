"use client";
export function FleetAiPlatAvailV2Panel({ monitors, active, uptime, downtime, nines }: { monitors: number; active: number; uptime: number; downtime: number; nines: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⬆️ AI Availability v2</h3>
    <div className="text-sm">{active}/{monitors} active · {uptime}% uptime · {downtime}m downtime · {"9".repeat(nines)} nines</div>
  </div>);
}
