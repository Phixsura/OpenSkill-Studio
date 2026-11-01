"use client";
export function FleetInngestPanel({ apps, active, functions, events }: { apps: number; active: number; functions: number; events: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Inngest</h3>
    <div className="text-sm">{active}/{apps} active · {functions} functions · {events.toLocaleString()} events</div>
  </div>);
}
