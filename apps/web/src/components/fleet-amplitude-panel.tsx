"use client";
export function FleetAmplitudePanel({ orgs, active, events, charts }: { orgs: number; active: number; events: number; charts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Amplitude</h3>
    <div className="text-sm">{active}/{orgs} active · {events.toLocaleString()} events · {charts} charts</div>
  </div>);
}
