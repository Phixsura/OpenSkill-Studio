"use client";
export function FleetAiPlatformValueV7Panel({ trackers, active, value, roi, hours }: { trackers: number; active: number; value: number; roi: number; hours: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💎 AI Platform Value v7</h3>
    <div className="text-sm">{active}/{trackers} active · ${value.toLocaleString()} value · {roi}% ROI · {hours.toLocaleString()}h saved</div>
  </div>);
}
